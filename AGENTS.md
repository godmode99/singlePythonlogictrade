อธิบายการทำงานของระบบเทรด
ความต้องการ
ลำดับการทำงานแบบ async/await มีการ try/catch แสดงการทำงาน process/success/error ผ่าน log แบบ best practice
การตั้งชื่อ order_id ใช้ symbol+unix time เช่น xauusdm1752322800

0. python main.py โดยใช้ค่าจาก config.json
1. fetch OHLCV, ยอดเงินในบัญชี balance data จาก mt5 เพิ่มข้อมูลไปในตาราง ถ้ายังไม่มีไฟล์ให้สร้างโดยตั้งชื่อไฟล์ว่า symbol_ohlcv เช่น xauusdm1752322800_ohlcv
2. calculate indicators โดยใช้ data จาก raw_ohlcv สร้างไฟล์ใหม่ โดยตั้งชื่อไฟล์ว่า symbol+unix time เช่น xauusdm1752322800_indicators
3. detect price pattern โดยใช้ data จาก raw_ohlcv สร้างไฟล์ใหม่ โดยตั้งชื่อไฟล์ว่า symbol+unix time เช่น xauusdm1752322800_pattern
4. identify regime โดยใช้ data จาก ohlcv, indicators และ price pattern โดยตั้งชื่อไฟล์ว่า symbol+unix time เช่น xauusdm1752322800_regime
5. confidence scoring โดยใช้ data จาก indicators และ price pattern โดยตั้งชื่อไฟล์ว่า symbol+unix time เช่น xauusdm1752322800_confidence
6. select logic trade จาก regime หา entry/tp/sl/pending_order โดย pending order มี [buy stop, buy limit, sell stopm sell limit] โดยตั้งชื่อไฟล์ว่า symbol+unix time เช่น xauusdm1752322800_logicTrade
7. คำนวน lot size จาก (((confidence_score คูณ max_risk_per_trade)/100) คูณ free margin)/100 โดยตั้งชื่อไฟล์ว่า symbol+unix time เช่น xauusdm1752322800_logicTrade โดยตั้งชื่อไฟล์ว่า symbol+unix time เช่น xauusdm1752322800_lotSize
8. create order สร้าง order สำหรับส่ง mt5 {symbol, entry, tp, sl, pending_order, volume, conmment} ส่ง mt5 algotrading โดยมีเงื่อนไข confidence > 50 & RR>1.5 ถึงส่ง order และ comment แสดงเหตุผลในการเข้า order โดยตั้งชื่อไฟล์ว่า symbol+unix time เช่น xauusdm1752322800
9. สร้าง notification ส่ง telegram
   ตัวอย่าง
   📅 2025-07-23T11:40:00.476543
   🏦 account:DEMO_ACCOUNT
   ✅ Fetching data:success Calculating indicators:success Detecting patterns:success Detecting regimes:success Generating signals:success Applying risk management:success Sending orders:success Logging trades:success
   📊 regime_type: 1m=uptrend, 5m=uptrend, 15m=uptrend, 1h=volatile, 4h=uptrend

⏰ order Timeframe: 1m
⚙️ logic_trade: scalp_1m
📌 order_id:xauusdm1m1753245600
💰 entry: 3427.478
🛑 sl: 3426.3012291715036
🎯 tp: 3429.8315416569935
🟢⬆️ pending_order_type:buy_stop
⭐️ confidence: 70

⚖️ risk_per_trade:0.7%
💵 lot:0.0
📈 rr:2.0000000000003864

⏰ order Timeframe: 5m
⚙️ logic_trade: skip
📌 order_id:xauusdm5m1753245600
💰 entry: none
🛑 sl: none
🎯 tp: none
🟢⬆️ pending_order_type:skip
⭐️ confidence: 80
⚠️ reason:tf confirm mismatch

⏰ order Timeframe: 15m
⚙️ logic_trade: trend_follow_15m
📌 order_id:xauusdm15m1753245600
💰 entry: 3427.478
🛑 sl: 3422.1584310916132
🎯 tp: 3438.117137816774
🟢⬆️ pending_order_type:buy_stop
⭐️ confidence: 85

⚖️ risk_per_trade:0.85%
💵 lot:0.0
📈 rr:2.0000000000000853

⏰ order Timeframe: 1h
⚙️ logic_trade: skip_low_confidence
📌 order_id:xauusdm1h1753245600
💰 entry: none
🛑 sl: none
🎯 tp: none
🟢⬆️ pending_order_type:skip
⭐️ confidence: 20
⚠️ reason:low confidence

⏰ order Timeframe: 4h
⚙️ logic_trade: trend_follow_4h
📌 order_id:xauusdm4h1753245600
💰 entry: 3427.478
🛑 sl: 3406.53840083079
🎯 tp: 3469.3571983384195
🟢⬆️ pending_order_type:buy_stop
⭐️ confidence: 60

⚖️ risk_per_trade:0.6%
💵 lot:0.0
📈 rr:1.9999999999999782

10. อัพเดท winRate report จาก raw_mt5_TradeHistory หาว่าแต่ละ win/lose มาจาก logic trade อะไร โดยใช้ send_order_to_mt5 ตัด order มาเทียบ ตัด order ที่ไม่ได้เข้า และส่งไป notification ทาง telegram โดย เป็นคนละ chatid หรือ chatbot

11. วนลูปทุก 5 นาที

config.json

1. แบ่งหมวดหมู่หรือจัดกลุ่มตามการตั้งค่าตาม modules และ main.py

วิธีการระบุ regime ในแต่ละ timeframe

1. แต่ละ timeframe มีค่า ohlcv, indicator และ price pattern ของตัวเอง
2. ใช้ regime rules ในการหา pattern ของแต่ละ regime จากค่าต่างๆ เพื่อระบุ regime type
3. สร้างกฎในการให้คะแนนความแข็งแรงของ regime ที่ระบุ โดยใช้เงื่อนไขความสอดคล้อง indicators ขัดกันเองไหม, price pattern ขัดกันเองไหม รวมคะแนน จาก indicators และ price pattern เช่น 15m | uptrend strong 60 scores| indicators 30 scores | price pattern 30 scores |

วิธีการให้คะแนน confidence

1. แต่ละ timeframe จะมี 1 regime
2. นำเอาค่า regime จากแต่ละ timeframe ทีใหญ่กว่าและเล็กกว่า
3. สร้างกฎให้คะแนน โดยประเมินว่าขัดแย้งหรือตามให้ confidence score

วิธีการเลือก logic trade

1. แต่ละ regime ของแต่ละ timeframe จะมี 1 logic trade เช่น 15m_uptrend
2. ภายใน 1 logic trade จะมีหลายเงื่อนไข เช่น pending order ที่จุดที่ราคาน่าจะกลับตัวสั้น, pending order ที่จุดที่ราคาน่าจะกลับตัวไกล, pending order ที่จุดที่ราคาน่าจะทะลุไปต่อ, pending order ที่จุดที่ราคาน่ากลับเข้ากรอบ
3. สร้างกฎในการเลือกแต่ละเงื่อนไขใน logic trade ของแต่ละ timeframe

วิธีการ send order ไป mt5

1. คำนวน lot size จาก (((confidence_score คูณ max_risk_per_trade)/100) คูณ free margin)/100
2. สร้าง order สำหรับส่งไป mt5 algo trading
3. หาก pending order ไม่สำหรับ ให้ adjust สลับคำสั่ง pending order limit <> stop
4. หาก สลับแล้วยังไม่สำเร็จ ให้แสดงค่าว่าเป็น failed
5. สรุปผลการทำงานไป telegram
