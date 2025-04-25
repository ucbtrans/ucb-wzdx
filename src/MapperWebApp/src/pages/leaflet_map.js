import React, { useState, useEffect, useRef, useCallback } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polygon, LayersControl, useMap, LayerGroup } from 'react-leaflet';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import dynamic from 'next/dynamic';
import { Resizable } from 're-resizable'; // Use re-resizable for simplicity
import * as osm_mapper from './osm_mapper';  // IMPORT YOUR osm_mapper.js FILE!

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
    iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png').default,
    iconUrl: require('leaflet/dist/images/marker-icon.png').default,
    shadowUrl: require('leaflet/dist/images/marker-shadow.png').default,
});



// --- Component for our map ---
function MyMap({ initialCenter, initialZoom, geoJsonData, selectedId, setMarkers, markers, polygonPositions, setPolygonPositions, streetName }) {
    const mapRef = useRef(null);
    const [mapStyle, setMapStyle] = useState('osm');
    const [addMarkerMode, setAddMarkerMode] = useState(false); // Track add marker mode


    const onEachFeature = (feature, layer) => {
        if (feature.properties && feature.properties.popupContent) {
            layer.bindPopup(feature.properties.popupContent);
        }
    };

    const handleMapClick = useCallback((e) => {
        if (addMarkerMode) {
            setMarkers([...markers, { position: [e.latlng.lat, e.latlng.lng] }]);
            setAddMarkerMode(false); // Turn off add marker mode after placing a marker.
        }
    }, [addMarkerMode, markers, setMarkers]);


    useEffect(() => {
      if (mapRef.current) {
        const map = mapRef.current;
        if (map) { // Check if map is not null
          map.on('click', handleMapClick);
        }

        return () => {
            if(map){
                map.off('click', handleMapClick);
            }
        };
      }

    }, [handleMapClick, mapRef]);

    useEffect(() => {
        if (geoJsonData && selectedId) {
          const coords = geoJsonData.geometry.coordinates;
          const newMarkers = coords.map(coord => ({ position: [coord[1], coord[0]] }));
          setMarkers(newMarkers);
          setPolygonPositions(newMarkers); // Update polygon with new markers

          const lats = coords.map(coord => coord[1]);
          const lons = coords.map(coord => coord[0]);

            if (lats.length > 0 && lons.length > 0) {
              const newCenter = [
                  lats.reduce((sum, lat) => sum + lat, 0) / lats.length,
                  lons.reduce((sum, lon) => sum + lon, 0) / lons.length
              ];

                if (mapRef.current) {
                    mapRef.current.setView(newCenter, 18);
                }
            }

        }
      }, [geoJsonData, selectedId, setMarkers, setPolygonPositions]);



    useEffect(() => {
        // Update polygon positions when markers change
        const newPolygonPositions = markers.map(marker => marker.position);
        setPolygonPositions(newPolygonPositions);
    }, [markers, setPolygonPositions]);

    const handleMarkerDrag = (index, e) => {
        const newMarkers = [...markers];
        newMarkers[index] = { position: [e.target.getLatLng().lat, e.target.getLatLng().lng] };
        setMarkers(newMarkers);
    };

    const toggleMapStyle = () => {
        setMapStyle(prevStyle => prevStyle === 'osm' ? 'satellite' : 'osm');
    };


    return (
        <>
        <MapContainer
            center={initialCenter}
            zoom={initialZoom}
            style={{ height: '1000px', width: '100%' }}
            whenCreated={(map) => { mapRef.current = map }}
            //onClick={handleMapClick}  // Attach click listener to the map
        >
            <LayersControl position="topleft">
                <LayersControl.BaseLayer checked={mapStyle === 'osm'} name="osm">
                    <TileLayer
                        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                        maxZoom={20}
                    />
                </LayersControl.BaseLayer>
                <LayersControl.BaseLayer checked={mapStyle === 'satellite'} name="satellite">
                    <TileLayer
                        url='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}'
                    />
                </LayersControl.BaseLayer>
             </LayersControl>


            <LayerGroup>
                {markers.map((marker, index) => (
                    <Marker
                        key={index}
                        position={marker.position}
                        draggable={true}
                        eventHandlers={{
                            dragend: (e) => handleMarkerDrag(index, e),
                        }}
                    >
                        {marker.popupContent && <Popup>{marker.popupContent}</Popup>}
                    </Marker>
                ))}
            </LayerGroup>

             <Polygon positions={polygonPositions} />

        </MapContainer>
            </>
    );
}

// Wrap with dynamic to disable SSR (Server-Side Rendering)
const DynamicMap = dynamic(() => Promise.resolve(MyMap), {
  ssr: false,
});


// --- Main App Component ---
function HomePage() {
    const initialCenter = [37.8715, -122.2730];
    const initialZoom = 5;
    const [selectedId, setSelectedId] = useState('Canada');
    const [geoJsonData, setGeoJsonData] = useState(null);
    const [jsonDataDisplay, setJsonDataDisplay] = useState('');
    const [markers, setMarkers] = useState([]);  // Store marker positions
    const [polygonPositions, setPolygonPositions] = useState([]);
    const [streetName, setStreetName] = useState('');
    const [addMarkerMode, setAddMarkerMode] = useState(false); // Track add marker mode
    const [jsonOutputWidth, setJsonOutputWidth] = useState(700);



    // --- Data Fetching ---
    useEffect(() => {
        const fetchData = async () => {
            try {
                const response = await fetch(`http://128.32.234.154:8900/api/wzd/events/${selectedId}`);
                if (!response.ok) {
                  throw new Error(`HTTP error! Status: ${response.status}`);
                }
                const data = await response.json();
                setGeoJsonData(data);
                setJsonDataDisplay(JSON.stringify(data, null, 2));
                if (data.properties && data.properties['core-details'] && data.properties['core-details'].properties && data.properties['core-details'].properties.properties && data.properties['core-details'].properties.properties.core_details) {
                    setStreetName(data.properties['core-details'].properties.properties.core_details.road_names);
                  } else {
                    setStreetName('');
                  }

            } catch (error) {
                console.error("Error fetching data:", error);
                setGeoJsonData(null); // Clear data on error
                setJsonDataDisplay(`Error fetching data: ${error.message}`);
            }
        };

        if (selectedId) {
            fetchData();
        }
    }, [selectedId]);


    const handleSave = () => {
        console.log("Save button clicked.  Markers:", markers);
        console.log("Save button clicked.  polygon:", polygonPositions);
        // Implement your save logic here.  Send data to a backend, etc.
    };

    const handleRefine = async () => {
        // You'll likely need a server-side endpoint to handle the refinement
        // using your osm_mapper functions.
        console.log("street Name", streetName);
        if (markers.length === 2) {
            // Convert to format expected by your buffer_linestring_geodesic function
            let positions = markers.map(marker => [marker.position[1], marker.position[0]]);
            let bufferedPositions = osm_mapper.buffer_linestring_geodesic(positions, 0.000001);

			const polygon = osm_mapper.create_shapely_polygon(bufferedPositions);
			const graph = osm_mapper.retrieve_scaled_street_graph(positions, polygon);
			const street_lst = osm_mapper.get_street_list_in_graph(graph);
			const street_feature = osm_mapper.get_feature(graph, streetName);
			const buffer_linestring = osm_mapper.buffer_linestring_geodesic(street_feature.geometry.coordinates, 3.6);

            //Convert back for leaflet display
            bufferedPositions = buffer_linestring.map(coord => [coord[1], coord[0]]);
            setPolygonPositions(bufferedPositions);

        // Update the markers for consistency, though this is optional
            const newMarkers = bufferedPositions.map(pos => ({ position: pos }));
            setMarkers(newMarkers);
        }
        else{
            alert('Refine can only be used with 2 markers!')
        }
    };


    const handleUndo = () => {
        setMarkers([]);
        setPolygonPositions([]);
    }
    const handlePublish = () => {
        // Implement publish logic (send data to another system, etc.)
        console.log("Publish button clicked");
    };

	const toggleAddMarkerMode = () => {
        setAddMarkerMode(!addMarkerMode); // Toggle the mode
    };

    const handleResizeJsonOutput = useCallback((e, { size }) => {
        setJsonOutputWidth(size.width);
    }, []);


    return (
        <div>
            <h1 style={{ textAlign: 'center', width: '100%' }}>Zone Mapping App</h1>
            <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '5px', marginBottom: '10px' }}>
               <button onClick={toggleAddMarkerMode} style={{ padding: '10px 15px', backgroundColor: addMarkerMode ? 'red' : 'grey'  }} >
                    {addMarkerMode ? 'Cancel Add' : 'Add Marker'}
                </button>
                <button onClick={() => setMapStyle(prevStyle => prevStyle === 'osm' ? 'satellite' : 'osm')} style={{ padding: '10px 15px' }}>Toggle Map</button>
                <button onClick={handleSave} style={{ padding: '10px 15px' }}>Save</button>
                <button onClick={handleRefine} style={{ padding: '10px 15px' }}>Refine</button>
                <button onClick={handlePublish} style={{ padding: '10px 15px' }}>Publish</button>
                <button onClick={handleUndo} style={{ padding: '10px 15px' }}>Undo</button>
            </div>

            <select value={selectedId} onChange={(e) => setSelectedId(e.target.value)} style={{ marginBottom: '10px' }}>
              {/*You should replace this with dynamic list of ids, fetched from your initial API request. */}
                <option value="Canada">Canada</option>
                <option value="5031393">5031393</option>
                <option value="5035235">5035235</option>
                <option value="5029997">5029997</option>
            </select>

            <div style={{ display: 'flex' }}>
                <div style={{ flex: 1 }}>
                  <DynamicMap
                    initialCenter={initialCenter}
                    initialZoom={initialZoom}
                    geoJsonData={geoJsonData}
                    selectedId={selectedId}
                    setMarkers={setMarkers}
                    markers={markers}
                    polygonPositions={polygonPositions}
                    setPolygonPositions={setPolygonPositions}
					streetName = {streetName}
                  />
                </div>

               <Resizable
                    size={{ width: jsonOutputWidth, height: '100%' }}
                    onResize={handleResizeJsonOutput}
                    style={{ border: '1px solid gray', padding: '10px' }}
                    enable={{ top:false, right:false, bottom:false, left:true, topRight:false, bottomRight:false, bottomLeft:false, topLeft:false }}
                >
                  <h2>GeoJSON Data</h2>
                  <pre style={{ overflow: 'auto', maxHeight: '950px' }}>{jsonDataDisplay}</pre>
                </Resizable>
              </div>

            <div>
                <h3>Stored Coordinates:</h3>
                {/* Basic display, you might want to format this better */}
                <ul>
                    {markers.map((marker, index) => (
                        <li key={index}>
                            Lat: {marker.position[0]}, Lon: {marker.position[1]}
                        </li>
                    ))}
                </ul>
            </div>
        </div>
    );
}

export default HomePage;