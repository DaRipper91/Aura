package com.aura.app

import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.location.Location
import android.location.LocationManager
import android.os.BatteryManager
import android.telephony.CellSignalStrength
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
        val batteryStatus: Intent? = IntentFilter(Intent.ACTION_BATTERY_CHANGED).let { filter ->
            context.registerReceiver(null, filter)
        }
        val level = batteryStatus?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryStatus?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        val batteryPct = level * 100 / scale.toFloat()
        
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
        val telephonyManager = context.getSystemService(Context.TELEPHONY_SERVICE) as TelephonyManager
        val signalInfo = JSONObject()
        signalInfo.put("network_type", getNetworkType(telephonyManager.networkType))
        telemetry.put("network", signalInfo)

        return telemetry.toString()
    }

    private fun getNetworkType(type: Int): String {
        return when (type) {
            TelephonyManager.NETWORK_TYPE_NR -> "5G"
            TelephonyManager.NETWORK_TYPE_LTE -> "4G/LTE"
            else -> "UNKNOWN"
        }
    }
}
