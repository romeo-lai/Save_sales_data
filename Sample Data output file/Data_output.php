<?php

// --------------------------------------------------
// Database connection
// --------------------------------------------------

$host = "localhost";
$username = "root";
$password = "";
$database = "temp_sales";

$conn = new mysqli($host, $username, $password, $database);

if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
}

// --------------------------------------------------
// SQL query
// --------------------------------------------------

$sql = "
SELECT
    item_sales.`FCODE`,
    GROUP_CONCAT(
        DISTINCT item_sales.`DESC1`
        ORDER BY item_sales.`DESC1`
        SEPARATOR ' | '
    ) AS DESC1_LIST,
    GROUP_CONCAT(
        DISTINCT item_sales.`DESC2`
        ORDER BY item_sales.`DESC2`
        SEPARATOR ' | '
    ) AS DESC2_LIST,
    SUM(item_sales.`QTY`) AS total_qty
FROM item_sales
GROUP BY item_sales.`FCODE`
HAVING SUM(item_sales.`QTY`) > 30
ORDER BY total_qty DESC
";

$result = $conn->query($sql);

if (!$result) {
    die("Query failed: " . $conn->error);
}

// --------------------------------------------------
// Set headers for CSV download
// --------------------------------------------------

header('Content-Type: text/csv; charset=utf-8');
header('Content-Disposition: attachment; filename=item_sales_export.csv');

// --------------------------------------------------
// Output CSV
// --------------------------------------------------

$output = fopen('php://output', 'w');

// Header row
fputcsv($output, [
    'FCODE',
    'DESC1_LIST',
    'DESC2_LIST',
    'TOTAL_QTY'
]);

// Data rows
while ($row = $result->fetch_assoc()) {
    fputcsv($output, [
        $row['FCODE'],
        $row['DESC1_LIST'],
        $row['DESC2_LIST'],
        $row['total_qty']
    ]);
}

// cleanup
fclose($output);
$conn->close();

exit;