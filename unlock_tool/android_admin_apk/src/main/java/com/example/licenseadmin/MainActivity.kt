package com.example.licenseadmin

import android.os.Bundle
import android.util.Base64
import android.widget.Button
import android.widget.EditText
import android.widget.TextView
import androidx.appcompat.app.AppCompatActivity
import org.json.JSONObject
import java.security.KeyFactory
import java.security.PrivateKey
import java.security.Signature
import java.security.spec.PKCS8EncodedKeySpec

class MainActivity : AppCompatActivity() {
    companion object {
        private const val PRIVATE_KEY_PEM = """
-----BEGIN PRIVATE KEY-----
MIIEvAIBADANBgkqhkiG9w0BAQEFAASCBKYwggSiAgEAAoIBAQDPdlDp/JH5oj6x
PsFB9f1H1dMIwwd2AHCmlKJie1GwXrr0u/p+bc7yOj0j2J0PEGBJPcbcR5Hp6hd3
O3MhCHc5obdVq+SK8JLnCjBHch5TN2jSqA5W2jAq30NF03rvhxOUomEmop/4A405
BmZ5dZN2Se5XievFFr9zIEZcn8AIxY7D9spJPBL2vPTUbXMPXHtzfQC8+IohThDH
E0qcDVUPQEGZEXfI8SVTUFnpNNc2/fe/i5237zdkR5k7SZIIqkpsCLTu6XzIIiyn
p7SeHpeLQXpQ/USE0r7MugGMB1a6sLAnkAf0+xWkDscSqbeldRMH2x5F2upZOcJj
6wcax1TRAgMBAAECggEATyE8yZK5hvLYYLij8+nEmrK3FJ926A5Q6WjF6zRIOzJW
suRELhbqGUAXc+W6OjWv1B/JCtoNkJ/mJWc6iX32I7hH+lhfCpOqJI+hTI79fBYl
WDwbhAsi1idkPGzmdhgaYtXwolDjHTEVm4uSaH9tKHAYhbEoiXscuOe1jryr/WvU
uHyUIqgG0XXW7lwAWsEIh0AOThT4t4eFcUFP0RJYI+rszUSEQqBVhdN0nxQ1WqAN
hZ8vYXnstSX+brSvw3JVlKuX0cWGvZY4iRS09rl76kfkeKuQf0bfif56+K9z00kf
zZkA2I/edG8Y5P3mSx/1vOgbasttm5O4o1gJNqUOtQKBgQD4KAXyNtOKo97LW7vp
cy9DPRec8UyytuGOBRtbQm2Q07I1fxdzLXccYJLjDuNTjyITNAOf4sadld/1yflI
5rDc9vJkN1YDUhrOwj4utkmoFinl9C+64gWE7HP8Wiv5S61veoQf0bfif56+K9z00kf
zZkA2I/edG8Y5P3mSx/1vOgbasttm5O4o1gJNqUOtQKBgQDWBQNC+kngKwCRinE3
HpWgQq32twBqZIhgoD8kOLzj8nErfSZBNAYiKRSNFL8SDSvYMoxVcyg68OZ9mBiO
74EqHwngn4QQ/9XMSIObZcN6T3UivZUGWvIGUrV0mN57utl6TmOiyxsKJZOT7lav
tPP1//l2T2JfcWuNa8mhNBpq7wKBgFPfAxN4IEstU3Gb0Yj3WzP4g/CRRYDpepZL
d5GChBF82zBlggF1jlpS8ZI4R/DH4ZZn8Amr1cERFJ634r8W6RPlissAQNvidhkH
YYjcJ0zeIM8Nlsws8/yXBiR2PYKGZ1nUKKcVLiuJQDDIzLAMb/+qVOTiUPvh4LD1
MClLvVx1AoGARGo5zrFf6E8W0W+mHW6jeiWWouWBNoGIrwrK5HNWvq+Dydkp33IX
+9eSAD9/jO+08lnGTpKPa7gSlleGkjqx2ZsudyXG/AAsgi80EvsG8BRyZ3afKvbr
o2XRJ8KubHMgjl58r0+qByZX9NQd1fFMg3keb9mUotoI/Z5VSDj1sPUCgYAQ9yAf
zMwwukrXm9eY/P5OlOwk6vazliqjh+KBiwDmmHkRn2+6EYarmRFGi3PH7QY3g3lD
gCcjDWn7ckVOIHPVxxaMDPMcClHeREktNWZQecUDwzoSyt1TAxtxLGd4+YTE0bmh
Flm0PRZb5CsTnNmtqscBoJPvlIYw2b9SsgkFLw==
-----END PRIVATE KEY-----"""

        private const val KEY_ALIAS = "license_private"
    }

    private lateinit var inputUser: EditText
    private lateinit var inputExpiry: EditText
    private lateinit var inputFeatures: EditText
    private lateinit var outputLicense: TextView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        inputUser = findViewById(R.id.inputUser)
        inputExpiry = findViewById(R.id.inputExpiry)
        inputFeatures = findViewById(R.id.inputFeatures)
        outputLicense = findViewById(R.id.outputLicense)
        val buttonGenerate: Button = findViewById(R.id.buttonGenerate)

        buttonGenerate.setOnClickListener {
            val user = inputUser.text.toString().trim()
            val expiry = inputExpiry.text.toString().trim()
            val features = inputFeatures.text.toString().split(',').map { it.trim() }.filter { it.isNotEmpty() }
            if (user.isEmpty() || expiry.isEmpty()) {
                outputLicense.text = "Please enter both user and expiry date."
                return@setOnClickListener
            }
            val payload = JSONObject().apply {
                put("user", user)
                put("expiry", expiry)
                put("features", features)
                put("license_id", "LIC-${System.currentTimeMillis()}")
            }
            outputLicense.text = generateLicenseToken(payload)
        }
    }

    private fun generateLicenseToken(payload: JSONObject): String {
        val privateKey = loadPrivateKey() ?: return "Unable to load private key"
        val jsonString = payload.toString()
        val signer = Signature.getInstance("SHA256withRSA")
        signer.initSign(privateKey)
        signer.update(jsonString.toByteArray(Charsets.UTF_8))
        val signatureBytes = signer.sign()
        val token = JSONObject().apply {
            put("payload", payload)
            put("signature", Base64.encodeToString(signatureBytes, Base64.NO_WRAP))
        }
        return Base64.encodeToString(token.toString().toByteArray(Charsets.UTF_8), Base64.NO_WRAP)
    }

    private fun loadPrivateKey(): PrivateKey? {
        val cleanPem = PRIVATE_KEY_PEM
            .replace("-----BEGIN PRIVATE KEY-----", "")
            .replace("-----END PRIVATE KEY-----", "")
            .replace("\n", "")
            .replace("\r", "")
            .replace(" ", "")
        val decoded = Base64.decode(cleanPem, Base64.DEFAULT)
        val keySpec = PKCS8EncodedKeySpec(decoded)
        return KeyFactory.getInstance("RSA").generatePrivate(keySpec)
    }
}
