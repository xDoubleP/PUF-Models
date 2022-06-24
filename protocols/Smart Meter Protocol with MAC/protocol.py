import SmartMeter
import HANAggregator


sm1 = SmartMeter.SmartMeter("1", 123, 456)
sm2 = SmartMeter.SmartMeter("2", 111, 222)
ha1 = HANAggregator.HANAggregator("Master")

# ha1.enroll(sm1)
# ha1.enroll(sm2)

smart_meters = [sm1, sm2]

encrypted_data = []
for sm in smart_meters:
    ed = sm.get_encrypted_data()
    encrypted_data.append(ed)


ha1.data_aggregation(encrypted_data)
