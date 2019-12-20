import unittest
import tomotoio.messages as tm
import tomotoio.data as td
import struct


class TestMessages(unittest.TestCase):
    def testDecodeToioIDReturnsPositionID(self):
        tid = tm.decodeToioID(bytes([0x01, 0xc5, 0x02, 0x7f, 0x01, 0x32, 0x01, 0xbc, 0x02, 0x82, 0x01, 0x33, 0x01]))
        self.assertIsInstance(tid, td.PositionID)
        self.assertTrue(tid.isPosition)
        self.assertEqual(tid.x, 709)
        self.assertEqual(tid.y, 383)
        self.assertEqual(tid.angle, 306)
        self.assertEqual(tid.sensorX, 700)
        self.assertEqual(tid.sensorY, 386)
        self.assertEqual(tid.sensorAngle, 307)

    def testDecodeToioIDReturnsStandardID(self):
        tid = tm.decodeToioID(bytes([0x02, 0x00, 0x00, 0x38, 0x00, 0x15, 0x00]))
        self.assertIsInstance(tid, td.StandardID)
        self.assertTrue(tid.isStandard)
        self.assertEqual(tid.value, 3670016)
        self.assertEqual(tid.angle, 21)

    def testDecodeToioIDReturnsMissedFromPositionID(self):
        tid = tm.decodeToioID(bytes([0x03]))
        self.assertIsInstance(tid, td.MissedID)
        self.assertTrue(tid.isMissed)
        self.assertEqual(tid.fromType, td.ToioIDType.POSITION)

    def testDecodeToioIDReturnsMissedFromStandardID(self):
        tid = tm.decodeToioID(bytes([0x04]))
        self.assertIsInstance(tid, td.MissedID)
        self.assertTrue(tid.isMissed)
        self.assertEqual(tid.fromType, td.ToioIDType.STANDARD)

    def testDecodeToioIDReturnsMissedFromInvalidType(self):
        tid = tm.decodeToioID(bytes([0xff, 0x01, 0x02]))
        self.assertIsInstance(tid, td.MissedID)
        self.assertTrue(tid.isMissed)
        self.assertEqual(tid.fromType, td.ToioIDType.INVALID)

    def testDecodeToioIDRaisesErrorForInvalidLength(self):
        self.assertRaises(struct.error, tm.decodeToioID, bytes([0x01, 0x01, 0x02]))

    def testDecodeMotion(self):
        m = tm.decodeMotion(bytes([0x01, 0x01, 0x00]))
        self.assertTrue(m.isLevel)
        self.assertFalse(m.collision)
        m = tm.decodeMotion(bytes([0x01, 0x00, 0x01]))
        self.assertFalse(m.isLevel)
        self.assertTrue(m.collision)

    def testDecodeButton(self):
        self.assertFalse(tm.decodeButton(bytes([0x01, 0x00])))
        self.assertTrue(tm.decodeButton(bytes([0x01, 0x80])))

    def testDecodeBattery(self):
        self.assertEqual(tm.decodeBattery(bytes([0x50])), 80)

    def testEncodeMotor(self):
        self.assertEqual(tm.encodeMotor(100, -20),
                         bytes([0x02, 0x01, 0x01, 0x64, 0x02, 0x02, 0x14, 0x00]))
        self.assertEqual(tm.encodeMotor(-100, 20, 0.1),
                         bytes([0x02, 0x01, 0x02, 0x64, 0x02, 0x01, 0x14, 0x0a]))

    def testEncodeLight(self):
        self.assertEqual(tm.encodeLight(20, 30, 40, 0.16),
                         bytes([0x03, 0x10, 0x01, 0x01, 0x14, 0x1e, 0x28]))

    def testEncodeLightPattern(self):
        self.assertEqual(tm.encodeLightPattern([td.Light(20, 30, 40, 0.3), td.Light(40, 60, 80, 0.6)], 3),
                         bytes([0x04, 0x03, 0x02, 0x1e, 0x01, 0x01, 0x14, 0x1e, 0x28, 0x3c, 0x01, 0x01, 0x28, 0x3c, 0x50]))

    def testEncodeLightOff(self):
        self.assertEqual(tm.encodeLightOff(), bytes([0x01]))

    def testEncodeSound(self):
        self.assertEqual(tm.encodeSound(5, 128), bytes([0x02, 0x05, 0x80]))

    def testEncodeSoundByNotes(self):
        self.assertEqual(tm.encodeSoundByNotes([td.Note(32, 0.3, 100), td.Note(64, 0.6, 200)], 5),
                         bytes([0x03, 0x05, 0x02, 0x1e, 0x20, 0x64, 0x3c, 0x40, 0xc8]))

    def testEncodeSoundOff(self):
        self.assertEqual(tm.encodeSoundOff(), bytes([0x01]))

    def testConfigProtocolVersion(self):
        self.assertEqual(tm.encodeConfigProtocolVersionRequest(), bytes([0x01, 0x00]))
        self.assertEqual(tm.decodeConfigProtocolVersionResponse(bytes([0x81, 0x00, 0x41, 0x42, 0x43, 0x44, 0x45, 0x46])),
                         "ABCDEF")

    def testConfigLevelThreshold(self):
        self.assertEqual(tm.encodeConfigLevelThreshold(10), bytes([0x05, 0x0a]))
        self.assertEqual(tm.encodeConfigLevelThreshold(90), bytes([0x05, 0x2d])) # cap at 45

    def testConfigCollisionThreshold(self):
        self.assertEqual(tm.encodeConfigCollisionThreshold(7), bytes([0x06, 0x07]))
        self.assertEqual(tm.encodeConfigCollisionThreshold(90), bytes([0x06, 0x0a])) # cap at 10


if __name__ == '__main__':
    unittest.main()
