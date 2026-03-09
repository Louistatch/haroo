import React, { useState, useMemo, useEffect, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { MapContainer, TileLayer, Marker, Popup, Circle, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import marketsData from "../data/markets.json";
import { me } from "../api/auth";

// Fix Leaflet default icon issue with bundlers
delete (L.Icon.Default.prototype as any)._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

const marketIcon = new L.Icon({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41],
});

const selectedIcon = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
  iconSize: [25, 41], iconAnchor: [12, 41], popupAnchor: [1, -34], shadowSize: [41, 41],
});

// User location icon (blue pulsing dot)
const userIcon = L.divIcon({
  className: "",
  html: `<div style="width:18px;height:18px;background:#3b82f6;border:3px solid white;border-radius:50%;box-shadow:0 0 0 6px rgba(59,130,246,0.25),0 2px 8px rgba(0,0,0,0.3);"></div>`,
  iconSize: [18, 18],
  iconAnchor: [9, 9],
});

interface Market {
  name: string;
  lat: number;
  lng: number;
}

interface MarketWithDistance extends Market {
  distance?: number; // km
}

const TOGO_CENTER: [number, number] = [8.6, 1.1];
const TOGO_BOUNDS: [[number, number], [number, number]] = [[6.0, -0.2], [11.2, 1.8]];

const REGIONS = [
  { name: "Toutes les régions", minLat: 0, maxLat: 99 },
  { name: "Savanes", minLat: 10.0, maxLat: 12.0 },
  { name: "Kara", minLat: 9.0, maxLat: 10.0 },
  { name: "Centrale", minLat: 8.0, maxLat: 9.0 },
  { name: "Plateaux", minLat: 7.0, maxLat: 8.0 },
  { name: "Maritime", minLat: 6.0, maxLat: 7.0 },
];

/** Haversine distance in km */
function haversineKm(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371;
  const dLat = ((lat2 - lat1) * Math.PI) / 180;
  const dLon = ((lon2 - lon1) * Math.PI) / 180;
  const a =
    Math.sin(dLat / 2) ** 2 +
    Math.cos((lat1 * Math.PI) / 180) * Math.cos((lat2 * Math.PI) / 180) * Math.sin(dLon / 2) ** 2;
  return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

function formatDistance(km: number): string {
  if (km < 1) return `${Math.round(km * 1000)} m`;
  if (km < 10) return `${km.toFixed(1)} km`;
  return `${Math.round(km)} km`;
}

function FlyToMarket({ lat, lng }: { lat: number; lng: number }) {
  const map = useMap();
  useEffect(() => { map.flyTo([lat, lng], 14, { duration: 1 }); }, [lat, lng, map]);
  return null;
}

function FlyToLocation({ lat, lng, zoom, onDone }: { lat: number; lng: number; zoom: number; onDone: () => void }) {
  const map = useMap();
  useEffect(() => {
    map.flyTo([lat, lng], zoom, { duration: 1.2 });
    const timer = setTimeout(onDone, 1300);
    return () => clearTimeout(timer);
  }, [lat, lng, zoom, map, onDone]);
  return null;
}

function MapIcon() {
  return (
    <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
      <path d="M10 17s-6-4.35-6-8.5a6 6 0 0112 0C16 12.65 10 17 10 17z" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="10" cy="8.5" r="2" stroke="currentColor" strokeWidth="1.5" />
    </svg>
  );
}

function SearchIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="7" cy="7" r="5" stroke="currentColor" strokeWidth="1.5" />
      <path d="M11 11l3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

function ListIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <path d="M2 4h12M2 8h12M2 12h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" />
    </svg>
  );
}

function NearbyIcon() {
  return (
    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
      <circle cx="8" cy="8" r="2" stroke="currentColor" strokeWidth="1.5" />
      <circle cx="8" cy="8" r="5" stroke="currentColor" strokeWidth="1.2" strokeDasharray="3 2" />
      <circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1" strokeDasharray="2 2" opacity="0.5" />
    </svg>
  );
}

export default function Markets() {
  const navigate = useNavigate();
  const [search, setSearch] = useState("");
  const [region, setRegion] = useState("Toutes les régions");
  const [selected, setSelected] = useState<Market | null>(null);
  const [showList, setShowList] = useState(false);
  const mapRef = useRef<any>(null);

  // Proximity state
  const [userPos, setUserPos] = useState<{ lat: number; lng: number } | null>(null);
  const [nearbyMode, setNearbyMode] = useState(false);
  const [geoLoading, setGeoLoading] = useState(false);
  const [geoError, setGeoError] = useState("");
  const [flyTarget, setFlyTarget] = useState<{ lat: number; lng: number; zoom: number } | null>(null);

  const isAuthenticated = Boolean(localStorage.getItem("access_token"));
  const markets: Market[] = marketsData as Market[];

  // Auto-load exploitation GPS for EXPLOITANT users
  useEffect(() => {
    if (!isAuthenticated) return;
    me().then((user: any) => {
      if (user.user_type === 'EXPLOITANT' && user.exploitant_profile?.coordonnees_gps) {
        const gps = user.exploitant_profile.coordonnees_gps;
        if (gps.lat && gps.lon) {
          const loc = { lat: parseFloat(gps.lat), lng: parseFloat(gps.lon) };
          setUserPos(loc);
          setNearbyMode(true);
          setShowList(true);
          setFlyTarget({ lat: loc.lat, lng: loc.lng, zoom: 10 });
        }
      }
    }).catch(() => {});
  }, [isAuthenticated]);

  const handleNearbyClick = useCallback(() => {
    if (!isAuthenticated) {
      navigate("/login");
      return;
    }

    if (nearbyMode) {
      // Toggle off
      setNearbyMode(false);
      setUserPos(null);
      setGeoError("");
      setFlyTarget(null);
      return;
    }

    if (!navigator.geolocation) {
      setGeoError("La géolocalisation n'est pas supportée par votre navigateur.");
      return;
    }

    setGeoLoading(true);
    setGeoError("");

    navigator.geolocation.getCurrentPosition(
      (pos) => {
        const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
        setUserPos(loc);
        setNearbyMode(true);
        setShowList(true);
        setGeoLoading(false);
        setFlyTarget({ lat: loc.lat, lng: loc.lng, zoom: 10 });
      },
      (err) => {
        setGeoLoading(false);
        if (err.code === err.PERMISSION_DENIED) {
          setGeoError("Accès à la localisation refusé. Activez-la dans les paramètres.");
        } else {
          setGeoError("Impossible d'obtenir votre position. Réessayez.");
        }
      },
      { enableHighAccuracy: true, timeout: 10000 }
    );
  }, [isAuthenticated, nearbyMode, navigate]);

  // Filtered + distance-enriched markets
  const filtered = useMemo(() => {
    const reg = REGIONS.find((r) => r.name === region) || REGIONS[0];
    let result: MarketWithDistance[] = markets
      .filter((m) => {
        const matchSearch = !search || m.name.toLowerCase().includes(search.toLowerCase());
        const matchRegion = region === "Toutes les régions" || (m.lat >= reg.minLat && m.lat < reg.maxLat);
        return matchSearch && matchRegion;
      })
      .map((m) => ({
        ...m,
        distance: userPos ? haversineKm(userPos.lat, userPos.lng, m.lat, m.lng) : undefined,
      }));

    // In nearby mode, sort by distance
    if (nearbyMode && userPos) {
      result.sort((a, b) => (a.distance ?? Infinity) - (b.distance ?? Infinity));
    }

    return result;
  }, [markets, search, region, userPos, nearbyMode]);

  function handleSelectMarket(m: Market) {
    setSelected(m);
    setShowList(false);
  }

  return (
    <div style={{ height: "calc(100vh - 64px)", display: "flex", flexDirection: "column", background: "var(--bg)" }}>
      {/* Top bar */}
      <div style={{ padding: "1rem 1.5rem", background: "var(--surface)", borderBottom: "1px solid var(--border)", display: "flex", alignItems: "center", gap: 12, flexWrap: "wrap" }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--primary)" }}>
          <MapIcon />
          <span style={{ fontWeight: 800, fontSize: "1.1rem", color: "var(--text)" }}>Marchés</span>
        </div>

        <div style={{ flex: 1, minWidth: 200, maxWidth: 400, position: "relative" }}>
          <div style={{ position: "absolute", left: 12, top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
            <SearchIcon />
          </div>
          <input
            type="text" placeholder="Rechercher un marché..." value={search}
            onChange={(e) => setSearch(e.target.value)}
            style={{ width: "100%", padding: "8px 12px 8px 36px", borderRadius: 10, border: "1.5px solid var(--border)", background: "var(--bg)", color: "var(--text)", fontSize: 14, outline: "none", boxSizing: "border-box" }}
            onFocus={(e) => (e.target.style.borderColor = "var(--primary)")}
            onBlur={(e) => (e.target.style.borderColor = "var(--border)")}
          />
        </div>

        <select
          value={region} onChange={(e) => setRegion(e.target.value)}
          style={{ padding: "8px 12px", borderRadius: 10, border: "1.5px solid var(--border)", background: "var(--bg)", color: "var(--text)", fontSize: 14, cursor: "pointer", outline: "none" }}
        >
          {REGIONS.map((r) => <option key={r.name} value={r.name}>{r.name}</option>)}
        </select>

        {/* Nearby button */}
        <button
          onClick={handleNearbyClick}
          disabled={geoLoading}
          style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "8px 14px", borderRadius: 10,
            border: nearbyMode ? "1.5px solid #3b82f6" : "1.5px solid var(--border)",
            background: nearbyMode ? "#3b82f6" : "var(--bg)",
            color: nearbyMode ? "#fff" : "var(--text)",
            fontSize: 13, fontWeight: 600, cursor: geoLoading ? "wait" : "pointer",
            opacity: geoLoading ? 0.7 : 1,
            transition: "all 0.2s",
          }}
        >
          {geoLoading ? (
            <div style={{ width: 14, height: 14, border: "2px solid currentColor", borderTop: "2px solid transparent", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
          ) : (
            <NearbyIcon />
          )}
          {geoLoading ? "Localisation..." : nearbyMode ? "Désactiver proximité" : "Marchés proches"}
        </button>

        <button
          onClick={() => setShowList(!showList)}
          style={{ display: "flex", alignItems: "center", gap: 6, padding: "8px 14px", borderRadius: 10, border: "1.5px solid var(--border)", background: showList ? "var(--primary)" : "var(--bg)", color: showList ? "#fff" : "var(--text)", fontSize: 13, fontWeight: 600, cursor: "pointer" }}
        >
          <ListIcon />
          {filtered.length} marchés
        </button>
      </div>

      {/* Geo error banner */}
      <AnimatePresence>
        {geoError && (
          <motion.div
            initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }}
            style={{ background: "rgba(239,68,68,0.08)", borderBottom: "1px solid rgba(239,68,68,0.2)", padding: "10px 1.5rem", display: "flex", alignItems: "center", justifyContent: "space-between", gap: 12, overflow: "hidden" }}
          >
            <span style={{ color: "#ef4444", fontSize: 13, fontWeight: 500 }}>{geoError}</span>
            <button onClick={() => setGeoError("")} style={{ background: "none", border: "none", color: "#ef4444", cursor: "pointer", fontWeight: 700, fontSize: 16, padding: 0 }}>×</button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Main content */}
      <div style={{ flex: 1, display: "flex", position: "relative", overflow: "hidden" }}>
        {/* Map */}
        <div style={{ flex: 1 }}>
          <MapContainer center={TOGO_CENTER} zoom={7} style={{ height: "100%", width: "100%" }} maxBounds={TOGO_BOUNDS} minZoom={6} ref={mapRef}>
            <TileLayer
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
            />

            {/* User position marker */}
            {userPos && nearbyMode && (
              <>
                <Marker position={[userPos.lat, userPos.lng]} icon={userIcon}>
                  <Popup><strong>📍 Votre position</strong></Popup>
                </Marker>
                <Circle center={[userPos.lat, userPos.lng]} radius={30000} pathOptions={{ color: "#3b82f6", fillColor: "#3b82f6", fillOpacity: 0.06, weight: 1.5, dashArray: "6 4" }} />
              </>
            )}

            {filtered.map((m, i) => (
              <Marker
                key={`${m.name}-${i}`}
                position={[m.lat, m.lng]}
                icon={selected?.name === m.name && selected?.lat === m.lat ? selectedIcon : marketIcon}
                eventHandlers={{ click: () => setSelected(m) }}
              >
                <Popup>
                  <div style={{ fontFamily: "inherit", minWidth: 140 }}>
                    <strong style={{ fontSize: 14 }}>{m.name}</strong>
                    {m.distance !== undefined && (
                      <div style={{ marginTop: 4, display: "flex", alignItems: "center", gap: 4, color: "#3b82f6", fontWeight: 600, fontSize: 13 }}>
                        <NearbyIcon /> {formatDistance(m.distance)}
                      </div>
                    )}
                    <div style={{ fontSize: 11, color: "#888", marginTop: 2 }}>
                      {m.lat.toFixed(4)}, {m.lng.toFixed(4)}
                    </div>
                  </div>
                </Popup>
              </Marker>
            ))}

            {selected && <FlyToMarket lat={selected.lat} lng={selected.lng} />}
            {flyTarget && <FlyToLocation lat={flyTarget.lat} lng={flyTarget.lng} zoom={flyTarget.zoom} onDone={() => setFlyTarget(null)} />}
          </MapContainer>
        </div>

        {/* Side list */}
        <AnimatePresence>
          {showList && (
            <motion.div
              initial={{ width: 0, opacity: 0 }} animate={{ width: 360, opacity: 1 }} exit={{ width: 0, opacity: 0 }}
              transition={{ duration: 0.25 }}
              style={{ height: "100%", background: "var(--surface)", borderLeft: "1px solid var(--border)", overflow: "hidden", flexShrink: 0 }}
            >
              <div style={{ height: "100%", overflowY: "auto", padding: "0.75rem" }}>
                <div style={{ fontSize: 12, color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", padding: "0.5rem 0.5rem 0.75rem", borderBottom: "1px solid var(--border)", marginBottom: "0.5rem", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span>{filtered.length} marché{filtered.length !== 1 ? "s" : ""}{nearbyMode ? " (par distance)" : ""}</span>
                  {nearbyMode && <span style={{ color: "#3b82f6", fontSize: 11 }}>📍 Proximité activée</span>}
                </div>

                {filtered.length === 0 && (
                  <div style={{ textAlign: "center", padding: "2rem 1rem", color: "var(--text-muted)", fontSize: 14 }}>
                    Aucun marché trouvé
                  </div>
                )}

                {filtered.map((m, i) => {
                  const isSelected = selected?.name === m.name && selected?.lat === m.lat;
                  return (
                    <button
                      key={`${m.name}-${i}`}
                      onClick={() => handleSelectMarket(m)}
                      style={{
                        width: "100%", textAlign: "left", padding: "10px 12px", borderRadius: 10,
                        border: isSelected ? "1.5px solid var(--primary)" : "1px solid transparent",
                        background: isSelected ? "rgba(22,163,74,0.06)" : "none",
                        cursor: "pointer", display: "flex", alignItems: "center", gap: 10,
                        marginBottom: 4, transition: "all 0.15s",
                      }}
                    >
                      <div style={{
                        width: 36, height: 36, borderRadius: 10,
                        background: isSelected ? "var(--primary)" : "var(--bg)",
                        border: isSelected ? "none" : "1px solid var(--border)",
                        display: "flex", alignItems: "center", justifyContent: "center",
                        color: isSelected ? "#fff" : "var(--text-muted)", flexShrink: 0, fontSize: 15,
                      }}>
                        🏪
                      </div>
                      <div style={{ minWidth: 0, flex: 1 }}>
                        <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                          {m.name}
                        </div>
                        <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                          {m.lat.toFixed(4)}, {m.lng.toFixed(4)}
                        </div>
                      </div>
                      {m.distance !== undefined && (
                        <div style={{
                          background: "rgba(59,130,246,0.1)", color: "#3b82f6",
                          padding: "3px 8px", borderRadius: "100px",
                          fontSize: 11, fontWeight: 700, whiteSpace: "nowrap", flexShrink: 0,
                        }}>
                          {formatDistance(m.distance)}
                        </div>
                      )}
                    </button>
                  );
                })}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
