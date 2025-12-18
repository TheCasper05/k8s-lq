/**
 * Node.js WebSocket Client Example for LQ Real-time Service
 *
 * Install dependencies:
 *   npm install ws
 *
 * Usage:
 *   node client.js <jwt-token>
 */

const WebSocket = require('ws');

// Configuration
const WS_URL = process.env.WS_URL || 'ws://localhost:8082/ws';
const JWT_TOKEN = process.argv[2];

if (!JWT_TOKEN) {
    console.error('Usage: node client.js <jwt-token>');
    process.exit(1);
}

// Connect to WebSocket
const wsUrl = `${WS_URL}?token=${encodeURIComponent(JWT_TOKEN)}`;
const ws = new WebSocket(wsUrl);

// Event handlers
ws.on('open', () => {
    console.log('✓ Connected to WebSocket server');
    console.log('---');

    // Send a test message
    const message = {
        type: 'message',
        payload: {
            text: 'Hello from Node.js client!',
            timestamp: new Date().toISOString()
        }
    };

    ws.send(JSON.stringify(message));
    console.log('→ Sent message:', message);

    // Send ping every 30 seconds
    setInterval(() => {
        if (ws.readyState === WebSocket.OPEN) {
            const ping = {
                type: 'ping',
                payload: { timestamp: new Date().toISOString() }
            };
            ws.send(JSON.stringify(ping));
            console.log('→ Sent ping');
        }
    }, 30000);
});

ws.on('message', (data) => {
    try {
        const message = JSON.parse(data.toString());
        console.log('← Received message:', JSON.stringify(message, null, 2));
        console.log('---');
    } catch (error) {
        console.log('← Received (raw):', data.toString());
    }
});

ws.on('error', (error) => {
    console.error('✗ WebSocket error:', error.message);
});

ws.on('close', (code, reason) => {
    console.log(`✗ Connection closed: ${code} - ${reason || 'No reason provided'}`);
    process.exit(0);
});

// Handle process termination
process.on('SIGINT', () => {
    console.log('\nClosing connection...');
    ws.close();
});

console.log('Connecting to:', WS_URL);
console.log('Using token:', JWT_TOKEN.substring(0, 20) + '...');
