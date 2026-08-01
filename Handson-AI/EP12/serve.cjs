// Tiny static server for previewing the combined deck (index.html).
// Uses __dirname so it doesn't depend on cwd. Run: node serve.cjs
const http = require("http");
const fs = require("fs");
const path = require("path");

http.createServer((req, res) => {
  const rel = req.url === "/" ? "/index.html" : req.url.split("?")[0];
  const file = path.join(__dirname, decodeURIComponent(rel));
  fs.readFile(file, (err, data) => {
    if (err) { res.writeHead(404); res.end("not found"); return; }
    res.writeHead(200, { "Content-Type": "text/html; charset=utf-8" });
    res.end(data);
  });
}).listen(8090, () => console.log("deck preview on :8090"));
