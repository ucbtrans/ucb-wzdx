import { polygon as turfPolygon, buffer, lineString } from '@turf/turf';
import * as OSM from 'osm-api'; // Use osm-api library
import { Graph } from 'graphology';
import { bidirectional } from 'graphology-shortest-path/unweighted';
import * as fs from 'fs'; // Import for file system use. Only if necessary, not preferrable in front end javascript


// Lane Width Constant Values (Approximations so may need to change in the future)
const laneWidth = 3.657; // 12 feet to meters


// --- Helper Functions ---

function createShapelyPolygonAuto(markers) {
    // Assuming markers is an array of [lon, lat] pairs.
    return turfPolygon([markers]); // Turf.js expects coordinates in GeoJSON order (lon, lat)
}


//For createShapelyPolygon, you can keep using the previous function. No change needed.

async function retrieveScaledStreetGraph(markers, shPolygon) {
  if (!shPolygon.geometry) { //Properly check if the polygon is valid.
    console.error("Polygon is invalid!");
    return null; // Or throw an error, depending on your needs.
  }

  const graph = new Graph({ type: 'multi' }); // Use Graphology's MultiDiGraph

  let count = 1;
  while (graph.nodes().length === 0) {
    try {
      // Use the osm-api library to fetch data
      const osmData = await OSM.getMapByPolygon(shPolygon.geometry.coordinates[0]);

      // Process nodes and ways from osmData
      const nodes = {};
      const ways = {};

      for (const element of osmData.elements) {
        if (element.type === 'node') {
          nodes[element.id] = {
            x: element.lon,
            y: element.lat,
            ...element.tags // Add any node tags as attributes
          };
        } else if (element.type === 'way') {
          ways[element.id] = {
            nodes: element.nodes,
            ...element.tags
          };
        }
      }
      // Add nodes to the graph
      for (const nodeId in nodes) {
        graph.addNode(nodeId, nodes[nodeId]);
      }
      // Add edges to the graph
      for (const wayId in ways) {
        const way = ways[wayId];
        const wayNodes = way.nodes;
        for (let i = 0; i < wayNodes.length - 1; i++) {
          graph.addEdge(wayNodes[i], wayNodes[i + 1], { wayId, ...way });
        }
      }

    } catch (error) {
      console.error("Error fetching or processing OSM data:", error);
      //return null;
    }

    const bufferDistance = 0.0006 ** count;
    // Correctly buffer a Turf.js polygon:
    shPolygon = buffer(shPolygon, bufferDistance, { units: 'degrees' });
    count++;

    if (count > 5) {
        console.warn("Exceeded maximum attempts to create graph.");
      break;
    }
  }

  return graph;
}

function generateGraphFromPolygon(shPolygon) {
    //This function is not needed anymore, as retrieveScaledStreetGraph now handles the logic.
}

//No change needed here, but you need to change where this is called from.
function plotStreetGraph(graph) {
  // osmnx plotting is not available in the browser.  You would need to use
  // a different library (like Leaflet) to visualize the graph.  This function
  // should be removed or commented out in the final browser-based version.

  // console.log("Plotting is not supported in this environment."); // Informative message
}

async function getStreetListInGraph(graph) {
    const edges = [];

    graph.forEachEdge((edge, attributes, source, target) => {
        // Access the 'name' attribute from your OSM data
        if (attributes.name) {
            edges.push(attributes.name);
        }
    });

    //Flatten and deduplicate the list
    const flattened = flatten(edges);
    const uniqueNames = [...new Set(flattened)];
    //console.log(uniqueNames);
    return uniqueNames;  // Return the unique street names
}


// Helper function to "flatten" arrays (handle cases where street names are lists)
function flatten(arr) {
  const flattened = [];

  function recurse(item) {
    if (Array.isArray(item)) {
      item.forEach(recurse);
    } else if (item != null) {  // Check for null/undefined
        flattened.push(item);
    }
  }
  arr.forEach(recurse);
  return flattened;
}


// The getFeature, getLaneCountFromFeature, and getTargetStreetCenterline
// functions need to be adapted to work with the Graphology graph structure.

function getFeature(graph, streetName) {
    let foundFeature = null;

    graph.forEachEdge((edge, attributes, source, target) => {
        // Access the 'name' attribute from your OSM data
        if (attributes.name) {
           if(checkFirstWordMatch(attributes.name, streetName)){
             foundFeature = {
                properties: attributes, //Contains necessary attributes
                geometry: { type: 'LineString',
                 coordinates: [
                    [graph.getNodeAttributes(source).x, graph.getNodeAttributes(source).y], //Source node
                    [graph.getNodeAttributes(target).x, graph.getNodeAttributes(target).y] //Target node
                ]}
              };
           }

        }
        if(foundFeature) return; //Short circuit forEachEdge once feature is found
    });
    return foundFeature;
}

function getLaneCountFromFeature(feature) {
    if (feature && feature.properties && feature.properties.lanes) {
        const laneCount = parseInt(feature.properties.lanes);
        return isNaN(laneCount) ? 0 : laneCount;
    }
    return 0; // Default to 0 if no lane count is found
}

function getTargetStreetCenterline(feature) {
    if(feature && feature.geometry && feature.geometry.coordinates){
        return feature.geometry.coordinates;
    }
    return []; //Return an empty array if there is no valid centerline
}


function checkFirstWordMatch(str1, str2) {
    if (!str1 || !str2) {  // Check for null or undefined
        return false;
    }
    if (!str1.trim() || !str2.trim()) { // Check for empty or whitespace-only
        return false;
    }

    const cleanStr1 = str1.replace(/[^a-zA-Z0-9]/g, '');
    const cleanStr2 = str2.replace(/[^a-zA-Z0-9]/g, '');

    const match1 = cleanStr1.match(/^\w+/); // Extract first word
    const match2 = cleanStr2.match(/^\w+/);

    if (match1 && match2) {
        return match1[0].toLowerCase() === match2[0].toLowerCase();
    } else {
        return false;
    }
}


//Simplified buffer function using turf.js
function buffer_linestring_geodesic(linestringCoords, bufferDistance) {
    const line = lineString(linestringCoords);
    const buffered = buffer(line, bufferDistance, { units: 'meters' });

     // Check if the buffered result is valid and has coordinates
    if (buffered && buffered.geometry && buffered.geometry.coordinates && buffered.geometry.coordinates.length > 0) {
		const simplified = turf.simplify(buffered, {tolerance: 0.00001, highQuality: false})
        return simplified.geometry.coordinates[0]; // Extract coordinates (outer ring)
    } else {
        console.warn("Buffering resulted in an invalid polygon or missing coordinates.");
        return []; // Return an empty array or handle the error as needed
    }
}

//This is not needed in javascript, as we handle projection using turf.js
function utm_zone(longitude) {
    //Not needed.
}


// Main refinement function (adapted for async/await)
async function refine_geometry(workzone_json) {

    let coordinates = workzone_json.geometry.coordinates;
    const targetStreetName = workzone_json.properties['core-details'].properties.properties.core_details.road_names;

    console.log("Original coordinates:", coordinates);

    let boundedCoords;
    if (coordinates.length === 2) {
        boundedCoords = buffer_linestring_geodesic(coordinates, 0.000001); //Small buffer to create a polygon
    } else if (coordinates.length > 2) {
        console.log("More than 2 points!");
        boundedCoords = coordinates;
    } else {
        console.warn("Not enough coordinates to refine."); // Handle edge case
        return workzone_json; //Return original json, since it cannot be handled.
    }

    // Create the polygon for graph retrieval.
    // Ensure correct coordinate order (longitude, latitude)
    const polygon = createShapelyPolygonAuto(boundedCoords.map(coord => [coord[0], coord[1]] ));

    const streetGraph = await retrieveScaledStreetGraph(coordinates, polygon);

    if (!streetGraph) {
        console.error("Failed to retrieve street graph.");
        return workzone_json;  // Return original or handle error appropriately
    }

    const streetList = await getStreetListInGraph(streetGraph); //Get street list
    const feature = getFeature(streetGraph, targetStreetName); //Find the specific street

    if(!feature) {
        console.error("Could not find target street in the graph.");
        return workzone_json;
    }
    const laneCount = getLaneCountFromFeature(feature);
    const centerline = getTargetStreetCenterline(feature);
    console.log("Centerline: ", centerline);

    //Buffer the centerline by total width (lanes * laneWidth)
    const refinedPolygonVertices = buffer_linestring_geodesic(centerline, laneCount * laneWidth);

    console.log("Refinement worked! Refined coordinates:", refinedPolygonVertices);
    workzone_json.geometry.coordinates = refinedPolygonVertices; //Update GeoJSON
    return workzone_json;
}

export {
    refine_geometry,
    createShapelyPolygonAuto,
    createShapelyPolygon,
    retrieveScaledStreetGraph,
    generateGraphFromPolygon,
    plotStreetGraph,
    getStreetListInGraph,
    flatten,
    getFeature,
    getLaneCountFromFeature,
    getTargetStreetCenterline,
    checkFirstWordMatch,
    buffer_linestring_geodesic,
    utm_zone,
 };