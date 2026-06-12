<?php
header('Content-Type: application/json');
header("Access-Control-Allow-Origin: *");
header("Access-Control-Allow-Methods: POST, GET, OPTIONS, PUT, DELETE");
header("Access-Control-Allow-Headers: Content-Type, Authorization, X-Requested-With");

date_default_timezone_set('Europe/London');

// Handle preflight requests
if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    http_response_code(200);
    exit;
}

// // Only allow POST
// if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
//     http_response_code(405);

//     echo json_encode([
//         'success' => false,
//         'message' => 'Method not allowed'
//     ]);

//     exit;
// }

try {

    // --------------------------------------------------
    // Database Config
    // --------------------------------------------------

    $host = 'localhost';
    $username = 'root';
    $password = '';
    $database = 'temp_sales';

    $conn = new mysqli(
        $host,
        $username,
        $password,
        $database
    );

    if ($conn->connect_error) {
        throw new Exception(
            'Database connection failed: ' .
            $conn->connect_error
        );
    }

    $conn->set_charset("utf8mb4");

    // --------------------------------------------------
    // Read JSON payload
    // --------------------------------------------------

    $rawInput = file_get_contents("php://input");

    $data = json_decode($rawInput, true);

    if (!$data) {
        throw new Exception('Invalid JSON payload');
    }

    if (!is_array($data)) {
        throw new Exception('Payload must be an array');
    }

    // --------------------------------------------------
    // Start transaction
    // --------------------------------------------------

    $conn->begin_transaction();

    // --------------------------------------------------
    // Prepare insert statement
    // --------------------------------------------------

    $stmt = $conn->prepare("
        INSERT INTO item_sales
        (
            FCODE,
            DESC1,
            DESC2,
            QTY,
            UNITPRICE,
            `DATE`,
            `TIME`
        )
        VALUES
        (
            ?, ?, ?, ?, ?, ?, ?
        )
    ");

    if (!$stmt) {
        throw new Exception(
            'Prepare failed: ' . $conn->error
        );
    }

    $inserted = 0;

    // --------------------------------------------------
    // Process rows
    // --------------------------------------------------

    foreach ($data as $row) {

        $fcode       = $row['FCODE'] ?? '';
        $desc1       = $row['DESC1'] ?? '';
        $desc2       = $row['DESC2'] ?? '';
        $qty         = $row['QTY'] ?? 0;
        $unitprice   = $row['UNITPRICE'] ?? 0;
        $date        = $row['DATE'] ?? null;
        $time        = $row['TIME'] ?? null;

        $stmt->bind_param(
            "sssddss",
            $fcode,
            $desc1,
            $desc2,
            $qty,
            $unitprice,
            $date,
            $time
        );

        if (!$stmt->execute()) {
            throw new Exception(
                'Insert failed: ' .
                $stmt->error
            );
        }

        $inserted++;
    }

    // --------------------------------------------------
    // Commit
    // --------------------------------------------------

    $conn->commit();

    echo json_encode([
        'success' => true,
        'inserted' => $inserted
    ]);

} catch (Exception $e) {

    if (isset($conn) && $conn instanceof mysqli) {
        $conn->rollback();
    }

    http_response_code(500);

    echo json_encode([
        'success' => false,
        'message' => $e->getMessage()
    ]);
}