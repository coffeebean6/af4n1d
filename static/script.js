document.addEventListener('DOMContentLoaded', function () {
    const enterpriseBtn = document.getElementById('enterprise-btn');
    const individualBtn = document.getElementById('individual-btn');
    const enterpriseSection = document.getElementById('enterprise-section');
    const individualSection = document.getElementById('individual-section');
    const citySelect = document.getElementById('city-select');
    const cityName = document.getElementById('city-name');
    const aqiValue = document.getElementById('aqi-value');
    const weatherDataTable = document.getElementById('weather-data');
    const predictBtn = document.getElementById('predict-btn');
    const predictionResult = document.getElementById('prediction-result');
    const predictionImg = document.getElementById('prediction-img');

    // Show/Hide sections based on user type selection
    enterpriseBtn.addEventListener('click', function () {
        enterpriseSection.classList.remove('hidden');
        individualSection.classList.add('hidden');
    });

    individualBtn.addEventListener('click', function () {
        individualSection.classList.remove('hidden');
        enterpriseSection.classList.add('hidden');
    });

    const today = new Date().toISOString().split('T')[0];
    const b1day = new Date(new Date().setDate(new Date().getDate() - 1)).toISOString().split('T')[0];
    const b2day = new Date(new Date().setDate(new Date().getDate() - 2)).toISOString().split('T')[0];

    // Dummy data for weather and pollution (This should come from an API)
    const weatherData = {
        "new-york": [
            { date: b2day, dewp: 25, wdsp: 12, max: 18, min: 9, prcp: 0, co: 0.3, no2: 55, o3: 0.054, pm10: 40, pm25: 25, so2: 17 },
            { date: b1day, dewp: 24, wdsp: 14, max: 20, min: 10, prcp: 0, co: 0.6, no2: 58, o3: 0.028, pm10: 45, pm25: 28, so2: 30 },
            { date: today, dewp: 23, wdsp: 16, max: 22, min: 12, prcp: 0, co: 0.4, no2: 17, o3: 0.086, pm10: 42, pm25: 26, so2: 42 }
        ],
        "london": [
            { date: b2day, dewp: 16, wdsp: 10, max: 15, min: 7, prcp: 1, co: 0.4, no2: 114, o3: 0.28, pm10: 35, pm25: 22, so2: 2 },
            { date: b1day, dewp: 15, wdsp: 12, max: 17, min: 8, prcp: 0.5, co: 0.3, no2: 116, o3: 0.3, pm10: 38, pm25: 24, so2: 2 },
            { date: today, dewp: 14, wdsp: 14, max: 19, min: 9, prcp: 0, co: 0.5, no2: 115, o3: 0.29, pm10: 37, pm25: 23, so2: 2 }
        ],
        "paris": [
            { date: b2day, dewp: 26, wdsp: 10, max: 15, min: 7, prcp: 1, co: 0.4, no2: 14, o3: 0.08, pm10: 35, pm25: 22, so2: 112 },
            { date: b1day, dewp: 25, wdsp: 12, max: 17, min: 8, prcp: 0.5, co: 0.3, no2: 16, o3: 0.07, pm10: 38, pm25: 24, so2: 123 },
            { date: today, dewp: 24, wdsp: 14, max: 19, min: 9, prcp: 0, co: 0.5, no2: 15, o3: 0.05, pm10: 37, pm25: 23, so2: 142 }
        ],
        // Add other cities here...
    };

    // Fetch current AQI based on selected city
    citySelect.addEventListener('change', function () {
        const city = citySelect.value;
        cityName.textContent = city.charAt(0).toUpperCase() + city.slice(1);
        aqiValue.textContent = `AQI: ${getCityAQI(city)}`;
        updateWeatherTable(city);
    });

    // Initial load for New York
    citySelect.value = "new-york";
    citySelect.dispatchEvent(new Event('change'));

    // Predict button click action
    predictBtn.addEventListener('click', async function () {
        const loadingIcon = document.getElementById('loadingIcon');
        // 显示加载图标
        loadingIcon.style.display = 'block';
        predictionResult.innerHTML = ``;
        predictionImg.innerHTML = ``;

        const city = citySelect.value;

        // Gather all weather data from the table
        const weatherData = [];
        const rows = document.querySelectorAll('#weather-data tr');
        rows.forEach(row => {
            const cells = row.querySelectorAll('td');
            weatherData.push({
                date: cells[0].textContent,
                dewp: cells[1].textContent,
                wdsp: cells[2].textContent,
                max: cells[3].textContent,
                min: cells[4].textContent,
                prcp: cells[5].textContent,
                co: cells[6].textContent,
                no2: cells[7].textContent,
                o3: cells[8].textContent,
                pm10: cells[9].textContent,
                pm25: cells[10].textContent,
                so2: cells[11].textContent,
            });
        });

        // Send data to the /predict endpoint
        try {
            const response = await fetch('/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ city, weatherData })
            });
            // 隐藏加载图标
            loadingIcon.style.display = 'none';
            
            const data = await response.json();

            // Update prediction result and image 
            predictionResult.innerHTML = `Prediction for ${data.date}: AQI will be <span style="color: ${data.fontColor}; font-weight: bold; background-color: ${data.healthyColor};">${data.aqi}</span>`;
            predictionImg.innerHTML = `<img src="${data.imageUrl}" alt="Prediction Image" />`;

        } catch (error) {
            console.error('Error predicting AQI:', error);
            predictionResult.textContent = 'Failed to get prediction.';
        }
    });

    // Get AQI for the selected city (This would normally come from an API)
    function getCityAQI(city) {
        // Placeholder, replace with real AQI data from an API
        const cityAQI = {
            "new-york": 45,
            "london": 38,
            "paris": 50
        };
        return cityAQI[city] || 0;
    }

    // Update weather and pollution table
    function updateWeatherTable(city) {
        const data = weatherData[city];
        weatherDataTable.innerHTML = data.map(row => `
            <tr>
                <td contenteditable="true">${row.date}</td>
                <td contenteditable="true">${row.dewp}</td>
                <td contenteditable="true">${row.wdsp}</td>
                <td contenteditable="true">${row.max}</td>
                <td contenteditable="true">${row.min}</td>
                <td contenteditable="true">${row.prcp}</td>
                <td contenteditable="true">${row.co}</td>
                <td contenteditable="true">${row.no2}</td>
                <td contenteditable="true">${row.o3}</td>
                <td contenteditable="true">${row.pm10}</td>
                <td contenteditable="true">${row.pm25}</td>
                <td contenteditable="true">${row.so2}</td>
            </tr>
        `).join('');
    }
});
