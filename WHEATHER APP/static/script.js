const form = document.getElementById("weather-form");
const cityInput = document.getElementById("city-input");
const locationBtn = document.getElementById("location-btn");
const loadingState = document.getElementById("loading-state");
const weatherContent = document.getElementById("weather-content");
const statusBanner = document.getElementById("status-banner");
const currentTime = document.getElementById("current-time");
const currentDate = document.getElementById("current-date");
const locationName = document.getElementById("location-name");
const weatherDescription = document.getElementById("weather-description");
const weatherIcon = document.getElementById("weather-icon");
const temperatureValue = document.getElementById("temperature-value");
const feelsLike = document.getElementById("feels-like");
const humidity = document.getElementById("humidity");
const windSpeed = document.getElementById("wind-speed");
const conditionName = document.getElementById("condition-name");
const forecastList = document.getElementById("forecast-list");

function updateClock() {
  const now = new Date();
  currentTime.textContent = now.toLocaleTimeString([], {
    hour: "2-digit",
    minute: "2-digit",
  });
  currentDate.textContent = now.toLocaleDateString([], {
    weekday: "long",
    day: "numeric",
    month: "long",
    year: "numeric",
  });
}

function setLoading(isLoading) {
  loadingState.classList.toggle("hidden", !isLoading);
  if (isLoading) {
    weatherContent.classList.add("hidden");
    hideError();
  }
}

function showError(message) {
  statusBanner.textContent = message;
  statusBanner.classList.remove("hidden");
}

function hideError() {
  statusBanner.classList.add("hidden");
  statusBanner.textContent = "";
}

function setTheme(theme) {
  document.body.className = `theme-${theme}`;
}

function renderForecast(items) {
  forecastList.innerHTML = items
    .map(
      (item) => `
        <article class="forecast-item">
          <div class="forecast-meta">
            <strong>${new Date(item.date).toLocaleDateString([], { weekday: "short" })}</strong>
            <span>${new Date(item.date).toLocaleDateString([], { day: "numeric", month: "short" })} • ${item.description}</span>
          </div>
          <img src="${item.icon_url}" alt="${item.description}" />
          <div class="forecast-temp">
            <strong>${item.temperature}°C</strong>
            <span>Feels ${item.feels_like}°C</span>
          </div>
        </article>
      `
    )
    .join("");
}

function renderWeather(data) {
  const { current, forecast } = data;

  locationName.textContent = `${current.city}, ${current.country}`;
  weatherDescription.textContent = current.description;
  weatherIcon.src = current.icon_url;
  weatherIcon.alt = current.description;
  temperatureValue.textContent = current.temperature;
  feelsLike.textContent = `${current.feels_like}°C`;
  humidity.textContent = `${current.humidity}%`;
  windSpeed.textContent = `${current.wind_speed} km/h`;
  conditionName.textContent = current.condition;
  renderForecast(forecast);
  setTheme(current.theme);

  weatherContent.classList.remove("hidden");
}

async function fetchWeather(query) {
  setLoading(true);

  try {
    const response = await fetch(`/api/weather?${query}`);
    const data = await response.json();

    if (!response.ok) {
      throw new Error(data.error || "Unable to fetch weather information.");
    }

    renderWeather(data);
  } catch (error) {
    showError(error.message);
  } finally {
    setLoading(false);
  }
}

form.addEventListener("submit", (event) => {
  event.preventDefault();
  const city = cityInput.value.trim();

  if (!city) {
    showError("Please enter a city name.");
    return;
  }

  fetchWeather(new URLSearchParams({ city }).toString());
});

locationBtn.addEventListener("click", () => {
  if (!navigator.geolocation) {
    showError("Geolocation is not supported in this browser.");
    return;
  }

  setLoading(true);
  navigator.geolocation.getCurrentPosition(
    (position) => {
      const query = new URLSearchParams({
        lat: position.coords.latitude.toString(),
        lon: position.coords.longitude.toString(),
      }).toString();
      fetchWeather(query);
    },
    () => {
      setLoading(false);
      showError("Location access was denied. Search by city instead.");
    },
    { enableHighAccuracy: true, timeout: 10000 }
  );
});

updateClock();
setInterval(updateClock, 1000);
fetchWeather(new URLSearchParams({ city: "Bengaluru" }).toString());
