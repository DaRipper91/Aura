package com.aura.app

import androidx.biometric.BiometricManager
import androidx.biometric.BiometricPrompt
import androidx.core.content.ContextCompat
import androidx.fragment.app.FragmentActivity
import java.util.concurrent.Executor

class BiometricHelper(private val activity: FragmentActivity) {
    private val executor: Executor = ContextCompat.getMainExecutor(activity)
    private val hapticHelper = HapticHelper(activity)
    private val securityHelper = SecurityHelper()

    fun authenticateForTool(toolName: String, challenge: String, onSuccess: (String) -> Unit, onError: (String) -> Unit) {
        val biometricManager = BiometricManager.from(activity)
        if (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG) == BiometricManager.BIOMETRIC_SUCCESS) {
            val promptInfo = BiometricPrompt.PromptInfo.Builder()
                .setTitle("Authorize Tool: $toolName")
                .setSubtitle("Biometric confirmation required for Hub execution")
                .setNegativeButtonText("Deny")
                .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                .build()

            val biometricPrompt = BiometricPrompt(activity, executor, object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    try {
                        val signature = securityHelper.signChallenge(challenge)
                        onSuccess(signature)
                    } catch (e: Exception) {
                        onError("Signing Failed: ${e.message}")
                    }
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    hapticHelper.biometricReject()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    onError(errString.toString())
                }
            })

            biometricPrompt.authenticate(promptInfo)
        } else {
            onError("Biometric authentication not supported on this device.")
        }
    }

    fun authenticate(onSuccess: () -> Unit) {
        val biometricManager = BiometricManager.from(activity)
        if (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG) == BiometricManager.BIOMETRIC_SUCCESS) {
            val promptInfo = BiometricPrompt.PromptInfo.Builder()
                .setTitle("Aura Vault Unlock")
                .setSubtitle("Authenticate to access secure history")
                .setNegativeButtonText("Cancel")
                .build()

            val biometricPrompt = BiometricPrompt(activity, executor, object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(result: BiometricPrompt.AuthenticationResult) {
                    super.onAuthenticationSucceeded(result)
                    onSuccess()
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    hapticHelper.biometricReject()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    if (errorCode != BiometricPrompt.ERROR_USER_CANCELED) {
                        hapticHelper.biometricReject()
                    }
                }
            })

            biometricPrompt.authenticate(promptInfo)
        } else {
            // Fallback for devices without biometrics
            onSuccess()
        }
    }
}
