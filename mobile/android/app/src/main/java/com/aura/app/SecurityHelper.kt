package com.aura.app

import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyPairGenerator
import java.security.KeyStore
import java.security.Signature
import java.util.Base64

/**
 * 🛡️ SENTINEL MANDATE: Cryptographic Security Helper.
 * Manages hardware-backed keys in the Android Keystore for tool authorization.
 */
class SecurityHelper {
    private val KEY_ALIAS = "aura_auth_key"
    private val KEYSTORE_NAME = "AndroidKeyStore"

    init {
        ensureKeyExists()
    }

    private fun ensureKeyExists() {
        val keyStore = KeyStore.getInstance(KEYSTORE_NAME).apply { load(null) }
        if (!keyStore.containsAlias(KEY_ALIAS)) {
            val kpg = KeyPairGenerator.getInstance(
                KeyProperties.KEY_ALGORITHM_EC, KEYSTORE_NAME
            )
            val parameterSpec = KeyGenParameterSpec.Builder(
                KEY_ALIAS,
                KeyProperties.PURPOSE_SIGN or KeyProperties.PURPOSE_VERIFY
            ).run {
                setDigests(KeyProperties.DIGEST_SHA256)
                setUserAuthenticationRequired(true) // 🔒 REQUIRES BIOMETRICS
                setUserAuthenticationValidityDurationSeconds(-1) // Always require prompt
                build()
            }
            kpg.initialize(parameterSpec)
            kpg.generateKeyPair()
        }
    }

    fun getPublicKey(): String {
        val keyStore = KeyStore.getInstance(KEYSTORE_NAME).apply { load(null) }
        val certificate = keyStore.getCertificate(KEY_ALIAS)
        return Base64.getEncoder().encodeToString(certificate.publicKey.encoded)
    }

    fun signChallenge(challenge: String): String {
        val keyStore = KeyStore.getInstance(KEYSTORE_NAME).apply { load(null) }
        val privateKey = keyStore.getKey(KEY_ALIAS, null) as java.security.PrivateKey
        
        val signature = Signature.getInstance("SHA256withECDSA").apply {
            initSign(privateKey)
            update(challenge.toByteArray())
        }
        
        return Base64.getEncoder().encodeToString(signature.sign())
    }
}
