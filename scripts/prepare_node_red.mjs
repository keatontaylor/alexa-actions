// Simulation adapter: preserve every exported Function and HTTP Request node.
// Only replace manual Inject and Debug with HTTP endpoints to drive/assert the flow.
import {readFileSync, writeFileSync} from 'node:fs';
const flow = JSON.parse(readFileSync(new URL('../home-assistant/node-red-launch.json', import.meta.url), 'utf8'));
const input = flow.find(node => node.type === 'inject');
Object.assign(input, {type: 'http in', url: '/simulate', method: 'post', upload: false});
const output = flow.find(node => node.type === 'debug');
Object.assign(output, {type: 'http response', statusCode: '', headers: {}});
writeFileSync(process.argv[2], JSON.stringify(flow));
