package com.aura.app

import android.content.Context
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager

/**
 * HapticHelper: Implements non-verbal telemetry rhythms for Aura Spokes.
 * Uses VibrationEffect.Composition (API 30+) for nuanced feedback.
 */
class HapticHelper(private val context: Context) {
    private val vibrator: Vibrator? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
        vibratorManager.defaultVibrator
    } else {
        @Suppress("DEPRECATION")
        context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
    }

    /**
     * STATE_AWAKENING: Deep thud + wobbly spin.
     * Signifies model load or hub wakeup.
     */
    fun stateAwakening() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && vibrator?.areAllPrimitivesSupported(
                VibrationEffect.Composition.PRIMITIVE_THUD,
                VibrationEffect.Composition.PRIMITIVE_SPIN
            ) == true
        ) {
            val effect = VibrationEffect.startComposition()
                .addPrimitive(VibrationEffect.Composition.PRIMITIVE_THUD)
                .addPrimitive(VibrationEffect.Composition.PRIMITIVE_SPIN, 0.8f, 100)
                .compose()
            vibrator.vibrate(effect)
        } else {
            // Fallback for older devices
            vibrator?.vibrate(VibrationEffect.createOneShot(150, VibrationEffect.DEFAULT_AMPLITUDE))
        }
    }

    /**
     * BIOMETRIC_REJECT: Quick double-drop.
     * Signifies access denied or gating active.
     */
    fun biometricReject() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && vibrator?.areAllPrimitivesSupported(
                VibrationEffect.Composition.PRIMITIVE_QUICK_FALL
            ) == true
        ) {
            val effect = VibrationEffect.startComposition()
                .addPrimitive(VibrationEffect.Composition.PRIMITIVE_QUICK_FALL)
                .addPrimitive(VibrationEffect.Composition.PRIMITIVE_QUICK_FALL, 1.0f, 50)
                .compose()
            vibrator?.vibrate(effect)
        } else {
            vibrator?.vibrate(VibrationEffect.createWaveform(longArrayOf(0, 50, 50, 50), -1))
        }
    }

    /**
     * SESSION_DISCONNECT: Sharp final snap.
     * Signifies Tailnet drop or shell termination.
     */
    fun sessionDisconnect() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && vibrator?.areAllPrimitivesSupported(
                VibrationEffect.Composition.PRIMITIVE_CLICK
            ) == true
        ) {
            val effect = VibrationEffect.startComposition()
                .addPrimitive(VibrationEffect.Composition.PRIMITIVE_CLICK)
                .compose()
            vibrator?.vibrate(effect)
        } else {
            vibrator?.vibrate(VibrationEffect.createOneShot(50, 255))
        }
    }

    /**
     * TOKEN_THRRUM: Continuous subtle feedback for streaming.
     */
    fun tokenThrum() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && vibrator?.areAllPrimitivesSupported(
                VibrationEffect.Composition.PRIMITIVE_TICK
            ) == true
        ) {
            val effect = VibrationEffect.startComposition()
                .addPrimitive(VibrationEffect.Composition.PRIMITIVE_TICK, 0.3f)
                .compose()
            vibrator?.vibrate(effect)
        } else {
            vibrator?.vibrate(VibrationEffect.createOneShot(10, 50))
        }
    }
}
