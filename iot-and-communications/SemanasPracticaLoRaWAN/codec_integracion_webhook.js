/**
 * ChirpStack v4 Codec para TTGO ( el ESP32 con LoRa WAN) LoRa GPS+BMP280
 * Payload: 12 bytes Big-Endian
 * lat_e7:int32 | lon_e7:int32 | alt_m:int16 | temp_centi:int16
 */

function decodeUplink(input) {
  var bytes = input.bytes;
  var fPort = input.fPort;

  if (fPort !== 1) {
    return { data: { error: "Invalid fPort" } };
  }

  if (bytes.length !== 12) {
    return { data: { error: "Invalid payload length" } };
  }

  // Decodificar Big-Endian int32 para lat_e7
  var lat_e7 = (bytes[0] << 24) | (bytes[1] << 16) | (bytes[2] << 8) | bytes[3];
  if (lat_e7 & 0x80000000) lat_e7 = lat_e7 - 0x100000000;
  var latitude = lat_e7 / 1e7;

  // Decodificar Big-Endian int32 para lon_e7
  var lon_e7 = (bytes[4] << 24) | (bytes[5] << 16) | (bytes[6] << 8) | bytes[7];
  if (lon_e7 & 0x80000000) lon_e7 = lon_e7 - 0x100000000;
  var longitude = lon_e7 / 1e7;

  // Decodificar Big-Endian int16 para alt_m
  var alt_m = (bytes[8] << 8) | bytes[9];
  if (alt_m & 0x8000) alt_m = alt_m - 0x10000;
  var altitude = alt_m;

  // Decodificar Big-Endian int16 para temp_centi
  var temp_centi = (bytes[10] << 8) | bytes[11];
  if (temp_centi & 0x8000) temp_centi = temp_centi - 0x10000;
  var temperature = temp_centi === 0x7FFF ? null : temp_centi / 100.0;

  return {
    data: {
      latitude: parseFloat(latitude.toFixed(7)),
      longitude: parseFloat(longitude.toFixed(7)),
      altitude: altitude,
      temperature: temperature,
      gps_valid: !(latitude === 0 && longitude === 0),
      payload_hex: bytes.map(function(x) { return (x < 16 ? '0' : '') + x.toString(16); }).join('')
    }
  };
}

function encodeDownlink(input) {
  return { bytes: [] };
}
