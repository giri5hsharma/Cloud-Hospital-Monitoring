"""Execute on the Azure VM to verify each accepted row appears via the deployed dashboard."""
import os,json,time,requests
from datetime import datetime,timezone
URL=os.environ['FUNCTION_URL']; KEY=os.environ['FUNCTION_KEY']
DASH='https://smartroom-dashboard-girish2517-e6f0bacpgwc8fqhy.centralindia-01.azurewebsites.net'
CASES=[('normal',22,50,1,'NORMAL'),('upper_normal_boundary',24,60,2,'NORMAL'),('lower_normal_boundary',20,40,0,'NORMAL'),('warning',25,65,3,'WARNING'),('critical',28,75,4,'CRITICAL'),('temperature_below_18',17.9,50,1,'CRITICAL'),('temperature_at_18',18,50,1,'WARNING'),('temperature_above_18',18.1,50,1,'WARNING'),('temperature_below_20',19.9,50,1,'WARNING'),('temperature_above_24',24.1,50,1,'WARNING'),('temperature_at_26',26,50,1,'WARNING'),('temperature_above_26',26.1,50,1,'CRITICAL'),('humidity_below_30',22,29.9,1,'CRITICAL'),('humidity_at_30',22,30,1,'WARNING'),('humidity_above_30',22,30.1,1,'WARNING'),('humidity_below_40',22,39.9,1,'WARNING'),('humidity_above_60',22,60.1,1,'WARNING'),('humidity_at_70',22,70,1,'WARNING'),('humidity_above_70',22,70.1,1,'CRITICAL'),('occupancy_at_capacity',22,50,3,'WARNING'),('occupancy_above_capacity',22,50,4,'CRITICAL'),('recovery',22,50,1,'NORMAL')]
results=[]
for name,t,h,o,expected in CASES:
 payload=dict(room_id='ROOM-01',timestamp_utc=datetime.now(timezone.utc).isoformat(),temperature_c=t,humidity_percent=h,occupancy=o)
 start=time.monotonic();r=requests.post(URL,json=payload,headers={'x-functions-key':KEY},timeout=45);ms=round((time.monotonic()-start)*1000)
 data=r.json();key=data.get('record',{}).get('RowKey');visible=False
 for attempt in range(3):
  response=requests.get(DASH+'/api/readings',timeout=30);response.raise_for_status()
  matches=[x for x in response.json()['records'] if x['RowKey']==key]
  visible=bool(matches and matches[0]['status']==expected)
  if visible:break
  time.sleep(1)
 item=dict(test=name,input=payload,expected=expected,actual=data.get('status'),http=r.status_code,record_id=key,dashboard_verified=visible,latency_ms=ms,passed=r.status_code==200 and data.get('status')==expected and visible)
 results.append(item);print(json.dumps(item),flush=True)
for name,patch in [('invalid_humidity',{'humidity_percent':101}),('fractional_occupancy',{'occupancy':1.5}),('invalid_timestamp',{'timestamp_utc':'bad'}),('invalid_room',{'room_id':"bad'room"}),('boolean_temperature',{'temperature_c':True})]:
 payload=dict(room_id='ROOM-01',timestamp_utc=datetime.now(timezone.utc).isoformat(),temperature_c=22,humidity_percent=50,occupancy=1);payload.update(patch)
 r=requests.post(URL,json=payload,headers={'x-functions-key':KEY},timeout=30)
 item=dict(test=name,expected=400,actual=r.status_code,passed=r.status_code==400);results.append(item);print(json.dumps(item),flush=True)
r=requests.post(URL,json={},timeout=30)
item=dict(test='missing_function_key',expected=401,actual=r.status_code,passed=r.status_code==401);results.append(item);print(json.dumps(item),flush=True)
open('cloud-test-results.json','w').write(json.dumps(results,indent=2))
print('RESULT',sum(x['passed'] for x in results),'/',len(results),flush=True)
raise SystemExit(0 if all(x['passed'] for x in results) else 1)
