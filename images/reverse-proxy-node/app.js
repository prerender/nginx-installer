const http = require('http');

const hostname = '0.0.0.0';
const port = 3000;

const server = http.createServer((req, res) => {
    res.statusCode = 200;
    res.setHeader('Content-Type', 'text/plain');
    res.end('Hello from Node.js!');
});

server.listen(port, hostname, () => {
    console.log(`Node.js app listening at http://${hostname}:${port}`);
});
