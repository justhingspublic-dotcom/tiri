// 人臉框偵測（macOS Vision）：board_photos.py 用來統一理監事肖像取景。
// 用法：facedetect <img> [<img>...]  → stdout JSON {path: {w, h, faces: [{x, y, w, h, conf}]}}（座標為 0–1、原點左上）
// board_photos.py 會自動 swiftc 編譯到快取目錄，不必手動建置。
import Foundation
import Vision
import ImageIO

var results: [String: Any] = [:]
for path in CommandLine.arguments.dropFirst() {
    guard let src = CGImageSourceCreateWithURL(URL(fileURLWithPath: path) as CFURL, nil),
          let cg = CGImageSourceCreateImageAtIndex(src, 0, nil) else { results[path] = ["error": "load"]; continue }
    let req = VNDetectFaceRectanglesRequest()
    let handler = VNImageRequestHandler(cgImage: cg, orientation: .up, options: [:])
    do { try handler.perform([req]) } catch { results[path] = ["error": "\(error)"]; continue }
    let faces = (req.results ?? []).map { f -> [String: Double] in
        let b = f.boundingBox
        return ["x": b.origin.x, "y": 1 - b.origin.y - b.height, "w": b.width, "h": b.height, "conf": Double(f.confidence)]
    }
    results[path] = ["w": cg.width, "h": cg.height, "faces": faces]
}
let data = try! JSONSerialization.data(withJSONObject: results, options: [.prettyPrinted, .sortedKeys])
print(String(data: data, encoding: .utf8)!)
