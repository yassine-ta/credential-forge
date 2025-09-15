#include <string>
#include <vector>
#include <random>
#include <regex>
#include <chrono>
#include <sstream>
#include <iomanip>
#ifdef OPENSSL_FOUND
#include <openssl/rand.h>
#include <openssl/sha.h>
#include <openssl/evp.h>
#endif

extern "C" {
    #include <Python.h>
}

class CredentialUtils {
private:
    std::mt19937 rng;
    
public:
    CredentialUtils() : rng(std::chrono::steady_clock::now().time_since_epoch().count()) {}
    
    std::string generate_random_string(size_t length, const std::string& charset) {
        std::uniform_int_distribution<> dist(0, charset.size() - 1);
        std::string result;
        result.reserve(length);
        
        for (size_t i = 0; i < length; ++i) {
            result += charset[dist(rng)];
        }
        return result;
    }
    
    std::string generate_hex_string(size_t length) {
        const std::string hex_chars = "0123456789abcdef";
        return generate_random_string(length, hex_chars);
    }
    
    std::string generate_base64_string(size_t length) {
        const std::string base64_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        return generate_random_string(length, base64_chars);
    }
    
    std::string generate_aws_access_key() {
        return "AKIA" + generate_base64_string(16);
    }
    
    std::string generate_aws_secret_key() {
        return generate_base64_string(40);
    }
    
    std::string generate_jwt_token() {
        // Header
        std::string header = R"({"alg":"HS256","typ":"JWT"})";
        
        // Payload
        std::string payload = R"({"sub":"user123","iat":)" + 
                             std::to_string(std::time(nullptr)) + 
                             R"(,"exp":)" + 
                             std::to_string(std::time(nullptr) + 3600) + "}";
        
        // Encode header and payload
        std::string encoded_header = base64_encode(header);
        std::string encoded_payload = base64_encode(payload);
        
        // Create signature (simplified)
        std::string signature = generate_hex_string(32);
        
        return encoded_header + "." + encoded_payload + "." + signature;
    }
    
    std::string generate_api_key() {
        return "sk-" + generate_hex_string(32);
    }
    
    std::string generate_database_password() {
        const std::string charset = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*";
        return generate_random_string(16, charset);
    }
    
    bool validate_credential_pattern(const std::string& credential, const std::string& pattern) {
        try {
            std::regex regex_pattern(pattern);
            return std::regex_match(credential, regex_pattern);
        } catch (const std::regex_error& e) {
            return false;
        }
    }
    
private:
    std::string base64_encode(const std::string& input) {
        const std::string chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
        std::string result;
        int val = 0, valb = -6;
        
        for (unsigned char c : input) {
            val = (val << 8) + c;
            valb += 8;
            while (valb >= 0) {
                result.push_back(chars[(val >> valb) & 0x3F]);
                valb -= 6;
            }
        }
        
        if (valb > -6) {
            result.push_back(chars[((val << 8) >> (valb + 8)) & 0x3F]);
        }
        
        while (result.size() % 4) {
            result.push_back('=');
        }
        
        return result;
    }
};

// Python C API functions
static PyObject* generate_credential_cpp(PyObject* self, PyObject* args) {
    const char* credential_type;
    const char* pattern = nullptr;
    
    if (!PyArg_ParseTuple(args, "s|s", &credential_type, &pattern)) {
        return nullptr;
    }
    
    CredentialUtils utils;
    std::string credential;
    
    if (std::string(credential_type) == "aws_access_key") {
        credential = utils.generate_aws_access_key();
    } else if (std::string(credential_type) == "aws_secret_key") {
        credential = utils.generate_aws_secret_key();
    } else if (std::string(credential_type) == "jwt_token") {
        credential = utils.generate_jwt_token();
    } else if (std::string(credential_type) == "api_key") {
        credential = utils.generate_api_key();
    } else if (std::string(credential_type) == "password") {
        credential = utils.generate_database_password();
    } else {
        PyErr_SetString(PyExc_ValueError, "Unsupported credential type");
        return nullptr;
    }
    
    // Validate against pattern if provided
    if (pattern && !utils.validate_credential_pattern(credential, std::string(pattern))) {
        // Retry with different random seed
        credential = utils.generate_aws_access_key(); // Simplified retry
    }
    
    return PyUnicode_FromString(credential.c_str());
}

static PyObject* validate_credential_cpp(PyObject* self, PyObject* args) {
    const char* credential;
    const char* pattern;
    
    if (!PyArg_ParseTuple(args, "ss", &credential, &pattern)) {
        return nullptr;
    }
    
    CredentialUtils utils;
    bool is_valid = utils.validate_credential_pattern(std::string(credential), std::string(pattern));
    
    return PyBool_FromLong(is_valid ? 1 : 0);
}

static PyMethodDef CredentialMethods[] = {
    {"generate_credential", generate_credential_cpp, METH_VARARGS, "Generate credential using C++"},
    {"validate_credential", validate_credential_cpp, METH_VARARGS, "Validate credential against pattern"},
    {nullptr, nullptr, 0, nullptr}
};

static struct PyModuleDef credentialmodule = {
    PyModuleDef_HEAD_INIT,
    "credential_utils",
    "Native credential generation utilities",
    -1,
    CredentialMethods
};

PyMODINIT_FUNC PyInit_credential_utils(void) {
    return PyModule_Create(&credentialmodule);
}
