import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'source/function'))
from rules import validate,classify_room
class RulesTest(unittest.TestCase):
 def test_normal_edges(self):
  for t in [20,24]:
   for h in [40,60]:self.assertEqual(classify_room(t,h,2)[0],'NORMAL')
 def test_warning_edges(self):
  for t in [18,19.9,24.1,26]:self.assertEqual(classify_room(t,50,1)[0],'WARNING')
  for h in [30,39.9,60.1,70]:self.assertEqual(classify_room(22,h,1)[0],'WARNING')
  self.assertEqual(classify_room(22,50,3)[0],'WARNING')
 def test_critical(self):
  for t,h,o in [(17.9,50,1),(26.1,50,1),(22,29.9,1),(22,70.1,1),(22,50,4)]:self.assertEqual(classify_room(t,h,o)[0],'CRITICAL')
 def test_invalid(self):
  base=dict(room_id='ROOM-01',timestamp_utc='2026-10-08T10:00:00Z',temperature_c=22,humidity_percent=50,occupancy=1)
  for field,value in [('occupancy',1.5),('occupancy',True),('humidity_percent',101),('temperature_c',float('nan')),('room_id',"bad'room"),('timestamp_utc','2026-10-08')]:
   with self.assertRaises(ValueError):validate({**base,field:value})
  for body in [[],None,{},'text']:
   with self.assertRaises(ValueError):validate(body)
 def test_valid(self):
  self.assertEqual(validate(dict(timestamp_utc='2026-10-08T10:00:00Z',temperature_c=22,humidity_percent=50,occupancy=1))['room_id'],'ROOM-01')
if __name__=='__main__':unittest.main(verbosity=2)
