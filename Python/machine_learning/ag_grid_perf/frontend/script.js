let gridApi;
let socket;
let lastUpdateCount = 0;

const gridOptions = {
    theme: "legacy",
    sideBar: true, // Enable Enterprise SideBar
    enableCharts: true, // Enable Enterprise Charts
    columnDefs: [
        { field: "id", headerName: "ID", width: 100, sortable: true },
        { field: "sector", headerName: "Sector", width: 140, rowGroup: true, enableRowGroup: true },
        { field: "region", headerName: "Region", width: 140, enableRowGroup: true, enablePivot: true },
        { field: "ticker", headerName: "Ticker", width: 120, filter: true },
        {
            field: "price",
            headerName: "Price",
            width: 120,
            aggFunc: 'avg',
            cellRenderer: (params) => {
                if (!params.value) return '';
                const color = params.value > 1000 ? '#4ade80' : '#f87171'; // Green or Red
                return `<span style="color:${color}; font-weight:bold;">$${params.value.toFixed(2)}</span>`;
            },
            enableCellChangeFlash: true
        },
        { field: "change", headerName: "Change %", width: 120, enableCellChangeFlash: true, aggFunc: 'avg' },
        { field: "volume", headerName: "Volume", width: 150, valueFormatter: p => p.value ? p.value.toLocaleString() : '', aggFunc: 'sum' },
        {
            field: "last_updated",
            headerName: "Last Updated",
            width: 200,
            valueFormatter: params => params.value ? new Date(params.value * 1000).toLocaleTimeString() : ''
        }
    ],
    defaultColDef: {
        resizable: true,
        sortable: true,
        flex: 1
    },
    autoGroupColumnDef: {
        headerName: "Group",
        minWidth: 200,
        cellRendererParams: {
            suppressCount: false
        }
    },
    rowData: null,
    getRowId: (params) => params.data.id.toString()
};

// Initialize Grid
document.addEventListener('DOMContentLoaded', () => {
    const gridDiv = document.querySelector('#grid-container');
    gridApi = agGrid.createGrid(gridDiv, gridOptions);

    // Update Rate Counter
    setInterval(() => {
        document.getElementById('updateRate').innerText = lastUpdateCount;
        lastUpdateCount = 0;
    }, 1000);
});

function startSimulation() {
    if (socket) {
        socket.close();
    }

    const rowCount = document.getElementById('rowCount').value;
    const frequency = document.getElementById('frequency').value;

    document.getElementById('status').innerText = "Connecting...";

    // Connect to FastAPI WebSocket
    socket = new WebSocket("ws://localhost:8000/ws");

    socket.onopen = () => {
        document.getElementById('status').innerText = "Connected";
        // Send config
        socket.send(JSON.stringify({ rowCount: rowCount, frequency: frequency }));
    };

    socket.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        // console.log("Received message type:", msg.type); // Uncomment for verbose debug

        if (msg.type === "initial") {
            console.log(`Received initial data payload: ${msg.data.length} rows`);
            try {
                gridApi.setGridOption('rowData', msg.data); // Use setGridOption for v31+ consistency
                console.log("Grid data set successfully");
                document.getElementById('actualRows').innerText = msg.data.length.toLocaleString();
            } catch (e) {
                console.error("Error setting row data:", e);
            }
        }
        else if (msg.type === "update") {
            if (lastUpdateCount === 0) {
                // Log the first update just to see if we got here without initial
                // console.log("Processing update packet");
            }
            // Apply Transaction Async is best for high freq updates
            gridApi.applyTransactionAsync({ update: msg.data });
            lastUpdateCount += msg.data.length;
        }
    };

    socket.onclose = () => {
        document.getElementById('status').innerText = "Disconnected";
    };

    socket.onerror = (error) => {
        console.error("WebSocket Error:", error);
        document.getElementById('status').innerText = "Error (Check Console)";
    };
}

function stopSimulation() {
    if (socket) {
        socket.close();
        socket = null;
    }
}
