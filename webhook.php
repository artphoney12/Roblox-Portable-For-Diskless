<?php
// webhook.php
// Menerima data JSON dari Pakasir
$input = file_get_contents('php://input');
$data = json_decode($input, true);

if (!$data && !empty($_POST)) {
    $data = $_POST;
    $input = json_encode($_POST);
}
if (!$data && !empty($_GET)) {
    $data = $_GET;
    $input = json_encode($_GET);
}

// Folder untuk menyimpan lisensi (harus writable)
$license_dir = __DIR__ . '/licenses';
if (!is_dir($license_dir)) {
    mkdir($license_dir, 0777, true);
}

// Log input webhook untuk keperluan debugging
// (Disarankan dihapus jika sudah di mode production agar log tidak menumpuk)
file_put_contents($license_dir . '/webhook_log.txt', date('Y-m-d H:i:s') . " - " . $input . "\n", FILE_APPEND);

if ($data && isset($data['order_id']) && isset($data['status'])) {
    $order_id = $data['order_id'];
    $status = strtolower($data['status']);
    
    // Asumsi status sukses dari Pakasir adalah 'success', 'paid', 'settlement', 'capture', atau 'completed'.
    if (strpos($order_id, 'hwid_') === 0 && ($status === 'success' || $status === 'paid' || $status === 'settlement' || $status === 'capture' || $status === 'completed')) {
        
        // Memastikan order_id memiliki awalan 'hwid_'
        if (strpos($order_id, 'hwid_') === 0) {
            $hwid_part = substr($order_id, 5); // Mengambil sisa string setelah 'hwid_'
            // Extract HWID and additional data (Name, Warnet)
            $parts = explode('_', $hwid_part);
            $hwid = $parts[0];
            
            // Extract extra data if available
            $donor_name = isset($parts[1]) && !is_numeric($parts[1]) ? $parts[1] : "Anonim";
            $warnet_name = isset($parts[2]) && !is_numeric($parts[2]) ? $parts[2] : "-";
            
            // Generate Lisensi
            $secret = "artphoney_super_secret_key";
            $license_key = strtoupper(md5($hwid . $secret));
            
            // Simpan ke file HWID.txt
            $file_path = $license_dir . '/' . $hwid . '.txt';
            file_put_contents($file_path, $license_key);
            
            // Simpan log rapi ke donors_history.txt
            $log_entry = date('Y-m-d H:i:s') . " | HWID: $hwid | Nama: $donor_name | Warnet: $warnet_name | Status: Sukses\n";
            file_put_contents($license_dir . '/donors_history.txt', $log_entry, FILE_APPEND);
            
            echo json_encode(["status" => "ok", "message" => "License generated for " . $hwid]);
            exit;
        }
    }
}

echo json_encode(["status" => "ignored"]);
?>
