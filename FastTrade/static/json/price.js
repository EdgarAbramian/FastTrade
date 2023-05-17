const https = require('https');

https.get('https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT', res => {
  let data = [];
  const headerDate = res.headers && res.headers.date ? res.headers.date : 'no response date';
  console.log('Status Code:', res.statusCode);
  console.log('Date in Response header:', headerDate);

  res.on('data', chunk => {
    data.push(chunk);
  });

  res.on('end', () => {
    console.log('Response ended: ');
    const users = JSON.parse(Buffer.concat(data).toString());
    console.log(users.symbol);
    
  });
}).on('error', err => {
  console.log('Error: ', err.message);
});

for(let i = 0; i < 10;i++){
    console.log(i);
}








