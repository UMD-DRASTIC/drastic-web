import unittest
import requests
from getpass import getpass
import json

USER = "jerome"
PASS = "jerome"

API_URL = "http://127.0.0.1/api/cdmi"


class CDMITestCase(unittest.TestCase):

    def setUp(self):
        self.api_url = API_URL
        self.auth = (USER, PASS)

    def get(self, path, headers={}, auth=""):
        if not auth:
            auth = self.auth
        r = requests.get("{}{}".format(self.api_url,
                                       path),
                         auth=auth,
                         headers=headers)
        return r

    def put(self, path, data={}, headers={}, auth=""):
        if not auth:
            auth = self.auth
        r = requests.put("{}{}".format(self.api_url,
                                       path),
                         data=data,
                         auth=auth,
                         headers=headers)
        return r

    def delete(self, path, headers={}, auth=""):
        if not auth:
            auth = self.auth
        r = requests.delete("{}{}".format(self.api_url,
                                          path),
                         auth=auth)
        return r

    def tearDown(self):
        pass

    def create_container(self, path="/TestContainer1/", data={}):
        headers = {
            "Accept": "application/cdmi-container",
            "Content-Type": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        return self.put(path, headers=headers, data=data)

    def delete_container(self, path="/TestContainer1/"):
        return self.delete(path)


class CDMI(CDMITestCase):


    def test_serverAuthenticationSuccess_BasicAuthentication(self):
        """Create a container with correct credentials"""
        res = self.create_container("/TestContainer1/")
        self.assertTrue(res.status_code == 201)
        self.delete_container("/TestContainer1/")
 
#     def test_serverAuthenticationSuccess_DigestAuthentication(self):
#         """To create a container with correct credentials"""
#         pass
 
    def test_serverAuthenticationFailure_BasicAuthentication(self):
        """Do not permit creation of a container when supplied with invalid
        credentials"""
        headers = {
            "Accept": "application/cdmi-container",
            "Content-Type": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        auth = ("InvalidUsername", "InvalidPassword")
        res = self.put("/TestContainer1/", headers=headers,
                       auth=auth)
        self.assertTrue(res.status_code == 401)
 
#     def test_serverAuthenticationFailure_DigestAuthentication(self):
#         """Do not permit creation of a container when supplied with invalid
#         credentials"""
#         pass
 
    def test_CDMI_Capability_Read_3R_1(self):
        """Read system-wide capabilities"""
        headers = {
            "Content-Type": "application/cdmi-capability",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/cdmi_capabilities/", headers)
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
        """Read a capability object"""
        res = self.create_container("/TestContainer1/")
        headers = {
            "Content-Type": "application/cdmi-capability",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/cdmi_capabilities/TestContainer1/", headers)
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
        self.delete_container("/TestContainer1/")
 
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
        headers = {
            "Accept": "application/cdmi-container",
            "Content-Type": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.put("/TestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 201)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("domainURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilitiesURI"))
        self.assertTrue(j.has_key("metadata"))
        self.assertTrue(j.has_key("completionStatus"))
        self.assertTrue(j.has_key("children"))
        self.delete_container("/TestContainer1/")
 
    def test_CDMI_Container_Create_1C_3(self):
        """Create a container within an existing container """
        res = self.create_container("/TestContainer1/")
        headers = {
            "Accept": "application/cdmi-container",
            "Content-Type": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.put("/TestContainer1/TestContainer2/", headers=headers)
        self.assertTrue(r.status_code == 201)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("domainURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilitiesURI"))
        self.assertTrue(j.has_key("metadata"))
        self.assertTrue(j.has_key("completionStatus"))
        self.assertTrue(j.has_key("children"))
        self.assertTrue(j.has_key("childrenrange"))
        self.delete_container("/TestContainer1/")
 
    def test_CDMI_Container_Create_1C_4(self):
        """Do not permit creation of a container with an invalid container
        name"""
        headers = {
            "Accept": "application/cdmi-container",
            "Content-Type": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.put("/cdmi_TestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 400)
 
    def test_CDMI_Container_Create_1C_5_1(self):
        """Do not permit creation of a container with an invalid header field
        """
        headers = {
            "Accept": "application/container",
            "Content-Type": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.put("/TestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 406)
 
#     def test_CDMI_Container_Create_1C_5_2(self):
#         """Do not permit creation of a container with an invalid header field
#         """
#         # TODO: What is the error in the header ?
#         headers = {
#             "Accept": "application/cdmi-container",
#             "Content-Type": "application/cdmi-container",
#             "X-CDMI-Specification-Version": 1.1
#         }
#         r = self.put("/TestContainer1/", headers=headers)
#         self.assertTrue(r.status_code == 406)
 
#     def test_CDMI_Container_Create_1C_9(self):
#         """Fail the creation of a container by using the reference field with
#         other fields"""
#         res = self.create_container("/TestContainer1/")
#         headers = {
#             "Accept": "application/cdmi-container",
#             "Content-Type": "application/cdmi-container",
#             "X-CDMI-Specification-Version": 1.1
#         }
#         data = {
#             "reference" : "/TestContainer1/",
#             "copy" : "/TestContainer1/"
#         }
#         r = self.put("/TestContainer2/",
#                      data=data,
#                      headers=headers)
#         self.assertTrue(r.status_code == 400)
#         self.delete_container("/TestContainer1/")
 
    def test_CDMI_Container_Create_1C_10(self):
        """Do not permit creation of a container without slashes in the URI"""
        headers = {
            "Accept": "application/cdmi-container",
            "Content-Type": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.put("/TestContainer1", headers=headers)
        self.assertTrue(r.status_code == 400)
 
#     def test_CDMI_Container_Create_1C_11(self):
#         """Create a container by copying an existing container"""
#         res = self.create_container("/TestContainer1/")
#         headers = {
#             "Accept": "application/cdmi-container",
#             "Content-Type": "application/cdmi-container",
#             "X-CDMI-Specification-Version": 1.1
#         }
#         data = {
#             "copy" : "/TestContainer1/"
#         }
#         r = self.put("/TestContainer2/",
#                      data=data,
#                      headers=headers)
#         self.assertTrue(r.status_code == 201)
#         j = r.json()
#         self.assertTrue(j.has_key("objectType"))
#         self.assertTrue(j.has_key("objectID"))
#         self.assertTrue(j.has_key("objectName"))
#         self.assertTrue(j.has_key("parentURI"))
#         self.assertTrue(j.has_key("domainURI"))
#         self.assertTrue(j.has_key("parentID"))
#         self.assertTrue(j.has_key("capabilitiesURI"))
#         self.assertTrue(j.has_key("metadata"))
#         self.assertTrue(j.has_key("completionStatus"))
#         self.assertTrue(j.has_key("children"))
#         self.assertTrue(j.has_key("childrenrange"))
#         # Test that TestContainer2/ is a copy of TestContainer1/
#         # Check that all fields and their values are reproduced correctly
#         self.delete_container("/TestContainer1/")
#         self.delete_container("/TestContainer2/")
 
#     def test_CDMI_Container_Create_1C_12(self):
#         """Move a container to a new URI"""
#         res = self.create_container("/TestContainer1/")
#         res = self.create_container("/TestContainer1/TestContainer2/")
#         headers = {
#             "Accept": "application/cdmi-container",
#             "Content-Type": "application/cdmi-container",
#             "X-CDMI-Specification-Version": 1.1
#         }
#         data = {
#             "move" : "/TestContainer1/TestContainer2/"
#         }
#         r = self.put("/TestContainer1/TestContainer3/",
#                      data=data,
#                      headers=headers)
#         self.assertTrue(r.status_code == 201)
#         j = r.json()
#         self.assertTrue(j.has_key("objectType"))
#         self.assertTrue(j.has_key("objectID"))
#         self.assertTrue(j.has_key("objectName"))
#         self.assertTrue(j.has_key("parentURI"))
#         self.assertTrue(j.has_key("domainURI"))
#         self.assertTrue(j.has_key("parentID"))
#         self.assertTrue(j.has_key("capabilitiesURI"))
#         self.assertTrue(j.has_key("metadata"))
#         self.assertTrue(j.has_key("completionStatus"))
#         self.assertTrue(j.has_key("children"))
#         self.assertTrue(j.has_key("childrenrange"))
#         # Test that TestContainer3/ was created and TestContainer2/ deleted
#         # Check that all fields and their values are reproduced correctly
#         self.delete_container("/TestContainer1/")
 
    def test_CDMI_Container_Read_1R_1(self):
        """Read  a container successfully"""
        res = self.create_container("/TestContainer1/")
        headers = {
            "Accept": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/TestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 200)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("domainURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilitiesURI"))
        self.assertTrue(j.has_key("metadata"))
        self.assertTrue(j.has_key("completionStatus"))
        self.assertTrue(j.has_key("children"))
        self.assertTrue(j.has_key("childrenrange"))
        self.delete_container("/TestContainer1/")
 
    def test_CDMI_Container_Read_1R_2(self):
        """Read a container by objectID"""
        res = self.create_container("/TestContainer1/")
        headers = {
            "Accept": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        res = self.get("/TestContainer1/", headers=headers)
        j = res.json()
        oid = j['objectID']
         
        r = self.get("/cdmi_objectid/{}/".format(oid),
                     headers=headers)
        self.assertTrue(r.status_code == 200)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("domainURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilitiesURI"))
        self.assertTrue(j.has_key("metadata"))
        self.assertTrue(j.has_key("completionStatus"))
        self.assertTrue(j.has_key("children"))
        self.assertTrue(j.has_key("childrenrange"))
        self.delete_container("/TestContainer1/")
 
    def test_CDMI_Container_Read_1R_4(self):
        """Read a container with an invalid header field"""
        res = self.create_container("/TestContainer1/")
        headers = {
            "Accept": "application/container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/TestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 406)
        self.delete_container("/TestContainer1/")
 
    def test_CDMI_Container_Read_1R_6(self):
        """Read a non-existent container"""
        headers = {
            "Accept": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/TestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 404)
 
    def test_CDMI_Container_Read_1R_7(self):
        """Read a container with limited fields"""
        res = self.create_container("/TestContainer1/")
        headers = {
            "Accept": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/TestContainer1/?objectType;objectID", headers=headers)
        j = r.json()
        self.assertTrue(r.status_code == 200)
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.delete_container("/TestContainer1/")
 
#     def test_CDMI_Container_Read_1R_9(self):
#         """Read a container without a "/" (slash) in URI"""
#         res = self.create_container("/TestContainer1/")
#         headers = {
#             "Accept": "application/cdmi-container",
#             "X-CDMI-Specification-Version": 1.1
#         }
#         r = self.get("/TestContainer1", headers=headers)
#         self.assertTrue(r.status_code == 301)
#         self.delete_container("/TestContainer1/")
 
    def test_CDMI_Container_Read_1R_10_1(self):
        """Read a container using percent escaping of reserved characters"""
        res = self.create_container("/@TestContainer1/")
        headers = {
            "Accept": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/%40TestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 200)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("domainURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilitiesURI"))
        self.assertTrue(j.has_key("metadata"))
        self.assertTrue(j.has_key("completionStatus"))
        self.assertTrue(j.has_key("children"))
        self.assertTrue(j.has_key("childrenrange"))
        self.delete_container("/@TestContainer1/")
 
    def test_CDMI_Container_Read_1R_10_2(self):
        """Read a container using percent escaping of reserved characters"""
        res = self.create_container("/:TestContainer1/")
        headers = {
            "Accept": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/%3ATestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 200)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("domainURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilitiesURI"))
        self.assertTrue(j.has_key("metadata"))
        self.assertTrue(j.has_key("completionStatus"))
        self.assertTrue(j.has_key("children"))
        self.assertTrue(j.has_key("childrenrange"))
        self.delete_container("/:TestContainer1/")
 
    def test_CDMI_Container_Read_1R_10_4(self):
        """Read a container using percent escaping of reserved characters"""
        res = self.create_container("/%3FTestContainer1/")
        headers = {
            "Accept": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/%3FTestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 200)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("domainURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilitiesURI"))
        self.assertTrue(j.has_key("metadata"))
        self.assertTrue(j.has_key("completionStatus"))
        self.assertTrue(j.has_key("children"))
        self.assertTrue(j.has_key("childrenrange"))
        self.delete_container("/%3FTestContainer1/")
 
    def test_CDMI_Container_Read_1R_10_5(self):
        """Read a container using percent escaping of reserved characters"""
        res = self.create_container("/%23TestContainer1/")
        headers = {
            "Accept": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/%23TestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 200)
        j = r.json()
        self.assertTrue(j.has_key("objectType"))
        self.assertTrue(j.has_key("objectID"))
        self.assertTrue(j.has_key("objectName"))
        self.assertTrue(j.has_key("parentURI"))
        self.assertTrue(j.has_key("domainURI"))
        self.assertTrue(j.has_key("parentID"))
        self.assertTrue(j.has_key("capabilitiesURI"))
        self.assertTrue(j.has_key("metadata"))
        self.assertTrue(j.has_key("completionStatus"))
        self.assertTrue(j.has_key("children"))
        self.assertTrue(j.has_key("childrenrange"))
        self.delete_container("/%23TestContainer1/")
 
#     def test_CDMI_Container_Read_1R_11_1(self):
#         """Read a container using percent escaping of reserved characters
#         in metadata"""
#         data = {"metadata": {"@user": "test"}}
#         res = self.create_container("/@TestContainer1/",
#                                     data=json.dumps(data))
#         headers = {
#             "Accept": "application/cdmi-container",
#             "X-CDMI-Specification-Version": 1.1
#         }
#         r = self.get("/%40TestContainer1/?metadata:%40user", headers=headers)
#         self.assertTrue(r.status_code == 200)
#         j = r.json()
#         self.assertTrue(j.has_key("metadata"))
#         self.assertTrue(j["metadata"]["@user"] == "test")
#         self.delete_container("/@TestContainer1/")
 
#     def test_CDMI_Container_Read_1R_11_2(self):
#         """Read a container using percent escaping of reserved characters
#         in metadata"""
#         data = {"metadata": {":user": "test"}}
#         res = self.create_container("/TestContainer1/",
#                                     data=json.dumps(data))
#         headers = {
#             "Accept": "application/cdmi-container",
#             "X-CDMI-Specification-Version": 1.1
#         }
#         r = self.get("/TestContainer1/?metadata:%40user", headers=headers)
#         self.assertTrue(r.status_code == 200)
#         j = r.json()
#         self.assertTrue(j.has_key("metadata"))
#         self.assertTrue(j["metadata"][":user"] == "test")
#         self.delete_container("/TestContainer1/")
 
#     def test_CDMI_Container_Read_1R_11_5(self):
#         """Read a container using percent escaping of reserved characters
#         in metadata"""
#         data = {"metadata": {"?user": "test"}}
#         res = self.create_container("/TestContainer1/",
#                                     data=json.dumps(data))
#         headers = {
#             "Accept": "application/cdmi-container",
#             "X-CDMI-Specification-Version": 1.1
#         }
#         r = self.get("/TestContainer1/?metadata:%3user", headers=headers)
#         self.assertTrue(r.status_code == 200)
#         j = r.json()
#         self.assertTrue(j.has_key("metadata"))
#         self.assertTrue(j["metadata"]["?user"] == "test")
#         self.delete_container("/TestContainer1/")

    def test_CDMI_Container_Read_1R_12(self):
        """Create a container via non-CDMI and read it via CDMI"""
        r = self.put("/TestContainer1/")
        headers = {
            "Accept": "application/cdmi-container",
            "X-CDMI-Specification-Version": 1.1
        }
        r = self.get("/TestContainer1/", headers=headers)
        self.assertTrue(r.status_code == 200)
        self.delete_container("/TestContainer1/")
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
    if not USER:
        # Request username from interactive prompt
        USER = raw_input("Please enter the user's username: ")
    if not PASS:
        # Request password from interactive prompt
            PASS = getpass("Password: ")
    unittest.TextTestRunner(verbosity=2).run(suite())