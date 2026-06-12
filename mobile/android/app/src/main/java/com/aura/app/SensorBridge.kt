package com.aura.app

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.location.Location
import android.location.LocationManager
import android.os.BatteryManager
import android.os.Build
import android.telephony.TelephonyManager
import org.json.JSONObject
import java.time.Instant

/**
 * 📡 FORGE MANDATE: Hardware Sensor Bridge.
 * Aggregates on-device telemetry (Power, Location, Signal) for the Hub.
 */
class SensorBridge(private val context: Context) {

    fun getTelemetry(fuzzed: Boolean = true): String {
        val telemetry = JSONObject()
        telemetry.put("device_id", android.os.Build.MODEL)
        telemetry.put("timestamp", Instant.now().toString())

        // 🔋 POWER STATUS
        val filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        val batteryStatus: Intent? = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            context.registerReceiver(null, filter, Context.RECEIVER_NOT_EXPORTED)
        } else {
            context.registerReceiver(null, filter)
        }
        
        val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        val batteryPct = if (scale > 0) (level * 100 / scale.toFloat()) else -1f
        
        val powerInfo = JSONObject()
        powerInfo.put("battery_level", batteryPct.toInt())
        powerInfo.put("is_charging", batteryStatus?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) == BatteryManager.BATTERY_STATUS_CHARGING)
        telemetry.put("power", powerInfo)

        // 🛰️ LOCATION (Fuzzed by default)
        try {
            val locationManager = context.getSystemService(Context.LOCATION_SERVICE) as LocationManager
            val lastLocation: Location? = locationManager.getLastKnownLocation(LocationManager.PASSIVE_PROVIDER)
            
            val locInfo = JSONObject()
            if (lastLocation != null) {
                var lat = lastLocation.latitude
                var lon = lastLocation.longitude
                
                if (fuzzed) {
                    lat = lat + (Math.random() - 0.5) / 100 // ~1km blur
                    lon = lon + (Math.random() - 0.5) / 100
                }
                
                locInfo.put("lat", lat)
                locInfo.put("lon", lon)
                locInfo.put("fuzzed", fuzzed)
            } else {
                locInfo.put("status", "NO_LOCK")
            }
            telemetry.put("location", locInfo)
        } catch (e: SecurityException) {
            telemetry.put("location", "PERMISSION_DENIED")
        }

        // 📶 NETWORK SIGNAL
        try {
            val telephonyManager = context.getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
            val signalInfo = JSONObject()
            val type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.N) {
                telephonyManager.dataNetworkType
            } else {
                telephonyManager.networkType
            }
            signalInfo.put("network_type", getNetworkType(type))
            telemetry.put("network", signalInfo)
        } catch (e: Exception) {
            telemetry.put("network", "UNKNOWN")
        }

        return telemetry.toString()
    }

    private fun getNetworkType(type: Int): String {
        return when (type) {
            TelephonyManager.NETWORK_TYPE_NR -> "5G"
            TelephonyManager.NETWORK_TYPE_LTE -> "4G/LTE"
            TelephonyManager.NETWORK_TYPE_WIFI -> "Wi-Fi" // Not standard for Telephony but useful
            else -> "CELLULAR_DATA"
        }
    }
}
