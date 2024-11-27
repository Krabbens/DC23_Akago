const { ZBClient } = require("zeebe-node");

// Credentials from .env or hardcoded
const CLIENT_ID = "tvxysvRpDv6MnMZtEmOcd7VT.E~HxsjU";
const CLIENT_SECRET =
    "mOqoizmOFatlUCKyN6Yk5IP2U.9qEc2hOHcgz8v4TxRvXKKQ5TJLy.JKZYZI6dzO";
const CLUSTER_ID = "eea87386-0393-4bbc-ad2e-a10a85bb2646";
const REGION = "bru-2";

const zbc = new ZBClient({
    camundaCloud: {
        clientId: CLIENT_ID,
        clientSecret: CLIENT_SECRET,
        clusterId: CLUSTER_ID,
        clusterRegion: REGION,
    },
});

zbc.createWorker({
    taskType: "calculate-age",
    taskHandler: async (job) => {
        const { birthDate } = job.variables;

        // Calculate age
        const today = new Date();
        const birthDateObj = new Date(birthDate);
        let age = today.getFullYear() - birthDateObj.getFullYear();
        const month = today.getMonth() - birthDateObj.getMonth();
        if (
            month < 0 ||
            (month === 0 && today.getDate() < birthDateObj.getDate())
        ) {
            age--;
        }

        console.log(`Calculated age: ${age}`);

        const isAdult = age >= 18;

        await job.complete({
            age: age,
            isAdult: isAdult,
        });
    },
});
