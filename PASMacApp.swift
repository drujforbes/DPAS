import SwiftUI
import WebKit
import AppKit
import Security

@main
struct PlexArtworkStudioApp: App {
    var body: some Scene {
        WindowGroup("Drucifer Plex Artwork Studio") {
            StudioView()
                .frame(minWidth: 1100, minHeight: 740)
        }
        .windowStyle(.titleBar)
    }
}

struct StudioView: NSViewRepresentable {
    func makeCoordinator() -> Coordinator { Coordinator() }
    func makeNSView(context: Context) -> WKWebView {
        let config = WKWebViewConfiguration()
        config.defaultWebpagePreferences.allowsContentJavaScript = true
        config.userContentController.add(context.coordinator, name: "pasNative")
        let webView = WKWebView(frame: .zero, configuration: config)
        context.coordinator.webView = webView
        webView.navigationDelegate = context.coordinator
        webView.uiDelegate = context.coordinator
        // Use the public WebKit API; the private KVC key "drawsBackground" can throw an Objective-C exception at launch.
        webView.underPageBackgroundColor = .clear
        guard let url = Bundle.main.url(forResource: "index", withExtension: "html") else {
            webView.loadHTMLString("<h2>Bundled editor not found</h2>", baseURL: nil)
            return webView
        }
        webView.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        return webView
    }
    func updateNSView(_ nsView: WKWebView, context: Context) {}

    final class Coordinator: NSObject, WKNavigationDelegate, WKUIDelegate, WKScriptMessageHandler {
        weak var webView: WKWebView?
        private var bundledEditorURL: URL? { Bundle.main.url(forResource: "index", withExtension: "html")?.standardizedFileURL }
        private func isBundledEditor(_ url: URL?) -> Bool {
            guard let url = url, url.isFileURL, let expected = bundledEditorURL else { return false }
            return url.standardizedFileURL == expected
        }
        private var repository: URL?
        private var scopedURL: URL?
        private let bookmarkKey = "PAS.RepositoryBookmark.v1"
        override init() {
            super.init()
            restoreRepository()
        }
        deinit { scopedURL?.stopAccessingSecurityScopedResource() }
        private func restoreRepository() {
            guard let data = UserDefaults.standard.data(forKey: bookmarkKey) else { return }
            var stale = false
            guard let url = try? URL(resolvingBookmarkData: data, options: [.withSecurityScope], relativeTo: nil, bookmarkDataIsStale: &stale) else { return }
            // Unsandboxed builds may return false even for an accessible folder.
            // Check filesystem access rather than assuming a security scope is mandatory.
            let accessing = url.startAccessingSecurityScopedResource()
            let folder = url.appendingPathComponent("Plex Artwork Studio", isDirectory: true)
            var isDirectory: ObjCBool = false
            guard FileManager.default.fileExists(atPath: folder.path, isDirectory: &isDirectory),
                  isDirectory.boolValue else {
                if accessing { url.stopAccessingSecurityScopedResource() }
                return
            }
            scopedURL = accessing ? url : nil
            repository = folder
            if stale, let renewed = try? url.bookmarkData(options: [.withSecurityScope], includingResourceValuesForKeys: nil, relativeTo: nil) {
                UserDefaults.standard.set(renewed, forKey: bookmarkKey)
            }
        }
        private func selectRepository(_ parent: URL) throws -> URL {
            // Unsandboxed builds do not require security-scoped access. Acquire it
            // when available, but rely on actual filesystem operations for validation.
            // A failed selection must leave the previous bookmark intact.
            let accessing = parent.startAccessingSecurityScopedResource()
            do {
                let folder = parent.appendingPathComponent("Plex Artwork Studio", isDirectory: true)
                for sub in folders {
                    try FileManager.default.createDirectory(at: folder.appendingPathComponent(sub, isDirectory: true), withIntermediateDirectories: true)
                }
                let bookmark = try parent.bookmarkData(options: [.withSecurityScope], includingResourceValuesForKeys: nil, relativeTo: nil)
                let previousScope = scopedURL
                scopedURL = accessing ? parent : nil
                repository = folder
                UserDefaults.standard.set(bookmark, forKey: bookmarkKey)
                previousScope?.stopAccessingSecurityScopedResource()
                return folder
            } catch {
                if accessing { parent.stopAccessingSecurityScopedResource() }
                throw error
            }
        }
        private let keychainService = "com.plexartworkstudio.openai"
        private func readAPIKey() -> String? {
            let q: [String: Any] = [kSecClass as String:kSecClassGenericPassword, kSecAttrService as String:keychainService, kSecAttrAccount as String:"api-key", kSecReturnData as String:true, kSecMatchLimit as String:kSecMatchLimitOne]
            var result: CFTypeRef?
            guard SecItemCopyMatching(q as CFDictionary, &result) == errSecSuccess, let data = result as? Data else { return nil }
            return String(data:data, encoding:.utf8)
        }
        private func storeAPIKey(_ value: String) -> Bool {
            let q: [String:Any] = [kSecClass as String:kSecClassGenericPassword, kSecAttrService as String:keychainService, kSecAttrAccount as String:"api-key"]
            // Clearing the key is explicit. Replacing it must not delete the
            // working credential before Keychain has accepted its replacement.
            if value.isEmpty {
                let status = SecItemDelete(q as CFDictionary)
                return status == errSecSuccess || status == errSecItemNotFound
            }
            let updates: [String: Any] = [
                kSecValueData as String: Data(value.utf8),
                kSecAttrAccessible as String: kSecAttrAccessibleAfterFirstUnlockThisDeviceOnly
            ]
            let updateStatus = SecItemUpdate(q as CFDictionary, updates as CFDictionary)
            if updateStatus == errSecSuccess { return true }
            if updateStatus != errSecItemNotFound { return false }
            var attributes = q
            attributes.merge(updates) { _, replacement in replacement }
            return SecItemAdd(attributes as CFDictionary, nil) == errSecSuccess
        }
        private func replyImage(_ id:String, base64:String) {
            guard let jsonData = try? JSONSerialization.data(withJSONObject:["id":id,"ok":true,"message":"Image ready","imageBase64":base64]), let json = String(data:jsonData,encoding:.utf8) else { return }
            DispatchQueue.main.async { self.webView?.evaluateJavaScript("window.pasNativeReply(\(json))",completionHandler:nil) }
        }
        private func requestImageEdit(id:String, image:String, prompt:String) {
            guard let key = readAPIKey(), !key.isEmpty else { reply(id,ok:false,message:"Configure the OpenAI API key first.");return }
            // Check encoded size before decoding: a malicious or corrupted editor payload
            // must not allocate arbitrarily large native buffers.
            guard image.utf8.count <= 27_000_000 else {
                reply(id,ok:false,message:"Input image exceeds the 20 MB upload limit.");return
            }
            let cleanedPrompt = prompt.trimmingCharacters(in:.whitespacesAndNewlines)
            guard !cleanedPrompt.isEmpty, cleanedPrompt.utf8.count <= 12_000 else {
                reply(id,ok:false,message:"Enter a prompt of 1–12,000 UTF-8 bytes.");return
            }
            guard let data = Data(base64Encoded:image), !data.isEmpty, data.count <= 20_000_000 else {
                reply(id,ok:false,message:"Input image is invalid or exceeds 20 MB.");return
            }
            // Browser sends PNG data; reject other formats before contacting the API.
            guard data.starts(with: [137,80,78,71,13,10,26,10]) else {
                reply(id,ok:false,message:"Only PNG source artwork is supported for cloud edits.");return
            }
            // Decode PNG before sending it to the API, limiting decompression and dimensions.
            guard data.count >= 33,
                  Array(data[12..<16]) == [73,72,68,82],
                  let bitmap = NSBitmapImageRep(data: data),
                  bitmap.pixelsWide > 0, bitmap.pixelsHigh > 0,
                  bitmap.pixelsWide <= 8192, bitmap.pixelsHigh <= 8192,
                  Int64(bitmap.pixelsWide) * Int64(bitmap.pixelsHigh) <= 40_000_000 else {
                reply(id,ok:false,message:"PNG is corrupt or exceeds the 40-megapixel / 8192-pixel dimension limit.");return
            }
            let boundary = "PASBoundary-" + UUID().uuidString
            var body = Data()
            func append(_ string:String) { body.append(Data(string.utf8)) }
            append("--\(boundary)\r\nContent-Disposition: form-data; name=\"model\"\r\n\r\ngpt-image-1\r\n")
            append("--\(boundary)\r\nContent-Disposition: form-data; name=\"prompt\"\r\n\r\n\(cleanedPrompt)\r\n")
            append("--\(boundary)\r\nContent-Disposition: form-data; name=\"size\"\r\n\r\nauto\r\n")
            append("--\(boundary)\r\nContent-Disposition: form-data; name=\"image[]\"; filename=\"artwork.png\"\r\nContent-Type: image/png\r\n\r\n")
            body.append(data)
            append("\r\n--\(boundary)--\r\n")
            var request = URLRequest(url:URL(string:"https://api.openai.com/v1/images/edits")!)
            request.httpMethod = "POST"
            request.setValue("Bearer \(key)",forHTTPHeaderField:"Authorization")
            request.setValue("multipart/form-data; boundary=\(boundary)",forHTTPHeaderField:"Content-Type")
            request.httpBody = body
            request.timeoutInterval = 180
            let session = URLSession(configuration: {
                let configuration = URLSessionConfiguration.ephemeral
                configuration.timeoutIntervalForRequest = 180
                configuration.timeoutIntervalForResource = 240
                return configuration
            }())
            session.dataTask(with:request) { responseData,response,error in
                if let error = error { self.reply(id,ok:false,message:"Image edit request failed: \(error.localizedDescription)");return }
                guard let responseData = responseData else { self.reply(id,ok:false,message:"Empty response");return }
                guard responseData.count < 35_000_000 else {
                    self.reply(id,ok:false,message:"OpenAI response exceeded the 35 MB safety limit.");return
                }
                // A gateway or service failure may return HTML/plain text rather
                // than JSON. Always report HTTP failures before decoding success data.
                guard let http = response as? HTTPURLResponse else {
                    self.reply(id,ok:false,message:"Image service returned no HTTP response.");return
                }
                if !(200...299).contains(http.statusCode) {
                    let errorObject = (try? JSONSerialization.jsonObject(with:responseData)) as? [String:Any]
                    let apiMessage = ((errorObject?["error"] as? [String:Any])?["message"] as? String)
                    // Never surface arbitrary HTML or response bodies to the editor.
                    let detail = apiMessage?.trimmingCharacters(in:.whitespacesAndNewlines)
                    let description = (detail?.isEmpty == false) ? String(detail!.prefix(400)) : "The image service rejected the request."
                    self.reply(id,ok:false,message:"HTTP \(http.statusCode): \(description)");return
                }
                guard let obj = (try? JSONSerialization.jsonObject(with:responseData)) as? [String:Any] else {
                    self.reply(id,ok:false,message:"Invalid JSON from image service (HTTP \(http.statusCode)).");return
                }
                guard let images = obj["data"] as? [[String:Any]], let b64 = images.first?["b64_json"] as? String else {self.reply(id,ok:false,message:"No image returned by API");return}
                // Validate actual generated image bytes before returning them to the editor.
                // Base64 decoding alone does not establish that the payload is an image.
                guard b64.utf8.count <= 33_000_000,
                      let decoded = Data(base64Encoded:b64),
                      !decoded.isEmpty, decoded.count <= 24_000_000,
                      decoded.starts(with: [137,80,78,71,13,10,26,10]),
                      decoded.count >= 33,
                      Array(decoded[12..<16]) == [73,72,68,82],
                      let resultImage = NSBitmapImageRep(data: decoded),
                      resultImage.pixelsWide > 0, resultImage.pixelsHigh > 0,
                      resultImage.pixelsWide <= 8192, resultImage.pixelsHigh <= 8192,
                      Int64(resultImage.pixelsWide) * Int64(resultImage.pixelsHigh) <= 40_000_000 else {
                    self.reply(id,ok:false,message:"Generated image is not a valid PNG or exceeds the 24 MB / 40-megapixel safety limits.");return
                }
                self.replyImage(id,base64:b64)
            }.resume()
        }
        private let folders = ["Posters", "Backgrounds", "Logos", "Source Artwork", "Projects"]
        private func reply(_ id: String, ok: Bool, message: String) {
            guard let data = try? JSONSerialization.data(withJSONObject: ["id":id,"ok":ok,"message":message]),
                  let json = String(data:data,encoding:.utf8) else { return }
            DispatchQueue.main.async { self.webView?.evaluateJavaScript("window.pasNativeReply(\(json))", completionHandler: nil) }
        }
        func userContentController(_ userContentController: WKUserContentController, didReceive message: WKScriptMessage) {
            // Never expose privileged native actions to remotely hosted pages or frames.
            // The bridge is available only to the bundled local editor.
            guard message.frameInfo.isMainFrame,
                  isBundledEditor(message.frameInfo.request.url),
                  isBundledEditor(webView?.url) else { return }
            guard message.name == "pasNative", let payload = message.body as? [String:Any],
                  let id = payload["id"] as? String, let action = payload["action"] as? String else {return}
            if action == "openaiKeyStatus" {
                reply(id,ok:true,message:readAPIKey() == nil ? "OpenAI API key not configured" : "OpenAI API key stored in macOS Keychain")
            } else if action == "setOpenaiKey" {
                guard let key = payload["key"] as? String, key.isEmpty || key.hasPrefix("sk-") else {reply(id,ok:false,message:"Enter a valid OpenAI API key.");return}
                let saved = storeAPIKey(key)
                reply(id,ok:saved,message:saved ? (key.isEmpty ? "OpenAI key cleared" : "OpenAI key saved securely in Keychain") : "Could not update macOS Keychain; existing credential was preserved.")
            } else if action == "openaiEdit" {
                guard let image = payload["image"] as? String, let prompt = payload["prompt"] as? String else {reply(id,ok:false,message:"Missing image or prompt");return}
                requestImageEdit(id:id,image:image,prompt:prompt)
            } else if action == "repositoryStatus" {
                if let repo = repository, FileManager.default.fileExists(atPath: repo.path) {
                    reply(id,ok:true,message:"Repository restored: \(repo.path)")
                } else {
                    reply(id,ok:false,message:"No accessible saved repository. Choose a folder.")
                }
            } else if action == "chooseRepository" {
                let panel = NSOpenPanel()
                panel.canChooseDirectories = true
                panel.canChooseFiles = false
                panel.canCreateDirectories = true
                panel.begin { result in
                    guard result == .OK, let parent = panel.url else { self.reply(id,ok:false,message:"Folder selection cancelled"); return }
                    let isDrive = (payload["storageMode"] as? String) == "drive"
                    let folder = parent.appendingPathComponent("Plex Artwork Studio",isDirectory:true)
                    do {
                        _ = try self.selectRepository(parent)
                        self.reply(id,ok:true,message:"\(isDrive ? "Google Drive synced" : "Local") repository ready: \(folder.path)\(isDrive ? " — syncing is managed by Google Drive for desktop" : "")")
                    } catch {self.reply(id,ok:false,message:"Could not create repository: \(error.localizedDescription)")}
                }
            } else if action == "writeFile" {
                guard let repo = repository, let dir = payload["directory"] as? String,
                      folders.contains(dir), let name = payload["filename"] as? String,
                      let encoded = payload["base64"] as? String,
                      // Reject oversized encoded payloads before allocating decoded data.
                      encoded.utf8.count <= 106_666_672,
                      let data = Data(base64Encoded:encoded), data.count < 80_000_000 else {
                    reply(id,ok:false,message:"Invalid file or repository not selected (80 MB limit)");return
                }
                let safe = name.replacingOccurrences(of:"[^a-zA-Z0-9._ -]",with:"_",options:.regularExpression)
                guard safe != ".", safe != "..", !safe.isEmpty, safe.count <= 150 else {reply(id,ok:false,message:"Invalid filename");return}
                do {
                    let root = repo.standardizedFileURL.resolvingSymlinksInPath()
                    let directory = repo.appendingPathComponent(dir, isDirectory:true)
                    // Do not follow a substituted symlink outside the selected repository.
                    let resolvedDirectory = directory.standardizedFileURL.resolvingSymlinksInPath()
                    guard resolvedDirectory.deletingLastPathComponent() == root else {
                        reply(id,ok:false,message:"Repository subfolder is not within the selected repository.");return
                    }
                    let target = resolvedDirectory.appendingPathComponent(safe)
                    // Atomic replacement of a symlink should not follow it, but explicitly
                    // reject symbolic-link destinations to avoid ambiguity and surprises.
                    if let values = try? target.resourceValues(forKeys:[.isSymbolicLinkKey]), values.isSymbolicLink == true {
                        reply(id,ok:false,message:"Refusing to overwrite a symbolic link.");return
                    }
                    try data.write(to:target,options:.atomic)
                    reply(id,ok:true,message:"Saved: \(target.path)")
                } catch {reply(id,ok:false,message:"Save failed: \(error.localizedDescription)")}
            }
        }

        func webView(_ webView: WKWebView, decidePolicyFor navigationAction: WKNavigationAction,
                     decisionHandler: @escaping (WKNavigationActionPolicy) -> Void) {
            // Keep remote content out of the privileged editor web view.
            // External artwork/provider pages open in the system browser.
            if let url = navigationAction.request.url,
               let scheme = url.scheme?.lowercased(),
               ["http", "https"].contains(scheme) {
                NSWorkspace.shared.open(url)
                decisionHandler(.cancel)
                return
            }
            if let url = navigationAction.request.url {
                if url.isFileURL && !isBundledEditor(url) {
                    decisionHandler(.cancel)
                    return
                }
                if let scheme = url.scheme?.lowercased(),
                   !["file", "about", "blob", "data"].contains(scheme) {
                    decisionHandler(.cancel)
                    return
                }
            }
            decisionHandler(.allow)
        }
        // JavaScript uses window.open(..., "_blank", "noopener,noreferrer") for
        // provider and evidence links. WKWebView does not create a new window
        // automatically: without this delegate those buttons silently do nothing.
        // Only the bundled editor may initiate a popup, and only HTTP(S) URLs
        // are handed to the user's default browser. Never create a privileged
        // second WKWebView for external content.
        func webView(_ webView: WKWebView,
                     createWebViewWith configuration: WKWebViewConfiguration,
                     for navigationAction: WKNavigationAction,
                     windowFeatures: WKWindowFeatures) -> WKWebView? {
            guard navigationAction.targetFrame == nil,
                  isBundledEditor(webView.url),
                  navigationAction.sourceFrame.isMainFrame,
                  isBundledEditor(navigationAction.sourceFrame.request.url),
                  let url = navigationAction.request.url,
                  let scheme = url.scheme?.lowercased(),
                  ["http", "https"].contains(scheme) else { return nil }
            NSWorkspace.shared.open(url)
            return nil
        }

        func webView(_ webView: WKWebView, runOpenPanelWith parameters: WKOpenPanelParameters,
                     initiatedByFrame frame: WKFrameInfo,
                     completionHandler: @escaping ([URL]?) -> Void) {
            // Only the bundled editor may request privileged native file selection.
            guard frame.isMainFrame, isBundledEditor(frame.request.url),
                  isBundledEditor(webView.url) else {
                completionHandler(nil)
                return
            }
            let panel = NSOpenPanel()
            panel.allowsMultipleSelection = parameters.allowsMultipleSelection
            panel.canChooseDirectories = parameters.allowsDirectories
            panel.canChooseFiles = true
            panel.begin { response in
                completionHandler(response == .OK ? panel.urls : nil)
            }
        }
    }
}
