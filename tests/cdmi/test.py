import unittest
import requests


# print r
#         print r.status_code
#         print r.headers
#         print r.text
#         print r.json()

class CDMITestCase(unittest.TestCase):

    def setUp(self):
        self.api_url = "http://127.0.0.1/cdmi"

    def get(self, path, headers={}):
        r = requests.get("{}{}".format(self.api_url,
                                       path),
                         headers=headers)
        return r

    def put(self, path, headers={}):
        r = requests.put("{}{}".format(self.api_url,
                                       path),
                         headers=headers)
        return r

    def tearDown(self):
        pass


class CDMI(CDMITestCase):


#     def test_serverAuthenticationSuccess_BasicAuthentication(self):
#         pass


#     def test_serverAuthenticationSuccess_DigestAuthentication(self):
#         pass


#     def test_serverAuthenticationFailure_BasicAuthentication(self):
#         pass


#     def test_serverAuthenticationFailure_DigestAuthentication(self):
#         pass


    def test_CDMI_Capability_Read_3R_1(self):
        """Read system-wide capabilities"""
        r = self.get("/cdmi_capabilities/",
                     {"X-CDMI-Specification-Version":"1.1"})
        self.assertTrue(r.status_code == 200)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilities"))
        self.assertTrue(j.has_key("childrenrange"))
        self.assertTrue(j.has_key("children"))

    def test_CDMI_Capability_Read_3R_2(self):
        """read a capability object"""
        r = self.get("/cdmi_capabilities/dataobject/",
                     {"X-CDMI-Specification-Version":"1.1"})
        self.assertTrue(r.status_code == 200)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilities"))
        self.assertTrue(j.has_key("childrenrange"))
        self.assertTrue(j.has_key("children"))

#     def test_CDMI_Capability_Read_3R_3(self):
#         """Read a capability object using objectID"""
#         pass

#     def test_CDMI_Capability_Read_3R_4(self):
#         """Update an existing capability object"""
#         pass

#     def test_CDMI_Capability_Read_3R_5(self):
#         """Delete a capability object"""
#         pass


    def test_CDMI_Container_Create_1C_1(self):
        """Create a container successfully"""
        r = self.put("/cdmi_capabilities/TestContainer1/",
                     {"X-CDMI-Specification-Version":"1.1"})
        print r.status_code
        self.assertTrue(r.status_code == 201)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        #self.assertTrue(j.has_key("domainURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilitiesURI"))
        self.assertTrue(j.has_key("metadata"))
        self.assertTrue(j.has_key("completionStatus"))
        self.assertTrue(j.has_key("children"))
        self.assertTrue(r.status_code == 200)

#     def test_CDMI_Container_Create_1C_3(self):
#         pass
# 
# 
#     def test_CDMI_Container_Create_1C_4(self):
#         pass
# 
# 
#     def test_CDMI_Container_Create_1C_5(self):
#         pass
# 
# 
#     def test_CDMI_Container_Create_1C_5_1(self):
#         pass
# 
# 
#     def test_CDMI_Container_Create_1C_5_2(self):
#         pass
# 
# 
#     def test_CDMI_Container_Create_1C_9(self):
#         pass
# 
# 
#     def test_CDMI_Container_Create_1C_10(self):
#         pass
# 
# 
#     def test_CDMI_Container_Create_1C_11(self):
#         pass
# 
# 
#     def test_CDMI_Container_Create_1C_12(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_1(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_2(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_4(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_6(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_7(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_9(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_10(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_10_1(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_10_2(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_10_4(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_10_5(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_11(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_11_1(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_11_2(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_11_4(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_11_5(self):
#         pass
# 
# 
#     def test_CDMI_Container_Read_1R_12(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_1(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_2(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_5(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_6(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_7(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_8(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_9(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_9_1(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_12(self):
#         pass
# 
# 
#     def test_CDMI_Container_Update_1U_13(self):
#         pass
# 
# 
#     def test_CDMI_Container_Delete_1D_1(self):
#         pass
# 
# 
#     def test_CDMI_Container_Delete_1D_2(self):
#         pass
# 
# 
#     def test_CDMI_Container_Delete_1D_3(self):
#         pass
# 
# 
#     def test_CDMI_Container_Delete_1D_4(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_1(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_3(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_6(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_7(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_8(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_9(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_10(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_11(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_12(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_14(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_15(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_16(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_17(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Create_2C_18(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_1(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_2_1(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_2_2(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_4(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_5(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_6_1(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_6_2(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_7(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_9(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_10(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_11(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_12(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_13(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_16(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_18(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Read_19(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_1(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_2_1(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_2_2(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_2_3(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_2_4(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_2_5(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_4(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_5(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_6(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Update_7(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Delete_1(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Delete_2(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Delete_3(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Delete_5(self):
#         pass
# 
# 
#     def test_CDMI_DataObject_Delete_6(self):
#         pass
# 
# 
#     def test_Container_Cleanup(self):
#         pass
# 
# 
#     def test_DataObject_Cleanup(self):
#         pass



# class NonCDMI(CDMITestCase):


#     def test_serverAuthentication(self):
#         pass
# 
# 
#     def test_Capability(self):
#         pass
# 
# 
#     def test_Container_Create_NC_1C_2(self):
#         pass
# 
# 
#     def test_Container_Create_NC_1C_3_1(self):
#         pass
# 
# 
#     def test_Container_Delete_NC_1D_1(self):
#         pass
# 
# 
#     def test_Container_Delete_NC_1D_2(self):
#         pass
# 
# 
#     def test_Container_Delete_NC_1D_4(self):
#         pass
# 
# 
#     def test_Container_Delete_NC_1D_5(self):
#         pass
# 
# 
#     def test_Container_Delete_NC_1D_6_1(self):
#         pass
# 
# 
#     def test_Container_Delete_NC_1D_6_2(self):
#         pass
# 
# 
#     def test_Container_Delete_NC_1D_6_3(self):
#         pass
# 
# 
#     def test_Container_Delete_NC_1D_7(self):
#         pass
# 
# 
#     def test_Container_Delete_NC_1D_8(self):
#         pass
# 
# 
#     def test_DataObject_Create_NC_2C_1(self):
#         pass
# 
# 
#     def test_DataObject_Create_NC_2C_2(self):
#         pass
# 
# 
#     def test_DataObject_Create_NC_2C_4(self):
#         pass
# 
# 
#     def test_DataObject_Create_NC_2C_5(self):
#         pass
# 
# 
#     def test_DataObject_Create_NC_2C_7(self):
#         pass
# 
# 
#     def test_DataObject_Read_NC_2R_1(self):
#         pass
# 
# 
#     def test_DataObject_Read_NC_2R_2(self):
#         pass
# 
# 
#     def test_DataObject_Read_NC_2R_3(self):
#         pass
# 
# 
#     def test_DataObject_Read_NC_2R_5(self):
#         pass
# 
# 
#     def test_DataObject_Read_NC_2R_6(self):
#         pass
# 
# 
#     def test_DataObject_Read_NC_2R_7(self):
#         pass
# 
# 
#     def test_DataObject_Read_NC_2R_9(self):
#         pass
# 
# 
#     def test_DataObject_Read_NC_2R_10(self):
#         pass
# 
# 
#     def test_DataObject_Update_NC_2U_1(self):
#         pass
# 
# 
#     def test_DataObject_Update_NC_2U_2(self):
#         pass
# 
# 
#     def test_DataObject_Update_NC_2U_3(self):
#         pass
# 
# 
#     def test_DataObject_Update_NC_2U_4(self):
#         pass
# 
# 
#     def test_DataObject_Update_NC_2U_7(self):
#         pass
# 
# 
#     def test_DataObject_Delete_NC_2D_1(self):
#         pass
# 
# 
#     def test_DataObject_Delete_NC_2D_2(self):
#         pass
# 
# 
#     def test_DataObject_Delete_NC_2D_3(self):
#         pass
# 
# 
#     def test_DataObject_Delete_NC_2D_4(self):
#         pass
# 
# 
#     def test_Server_Cleanup_Process(self):
#         pass
# 
# 
#     def test_Non_CDMI_Container_Cleanup(self):
#         pass
# 
#     def test_Non_CDMI_DataObject_Cleanup(self):
#         pass



def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(CDMI))
#    suite.addTest(unittest.TestLoader().loadTestsFromTestCase(NonCDMI))
    return suite


if __name__ == "__main__":
    unittest.TextTestRunner(verbosity=2).run(suite())