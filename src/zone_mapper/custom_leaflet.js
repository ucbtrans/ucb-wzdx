L.CircleMarker.include({
    _initInteraction: function () {
        L.CircleMarker.prototype._initInteraction.call(this);
        this.on('mousedown', this._onMouseDown, this);
    },
    _onMouseDown: function (e) {
        var leafletMap = this._map; // Get the map object
        leafletMap.dragging.disable(); // Disable map dragging
        leafletMap.on('mousemove', this._onMouseMove, this);
        leafletMap.on('mouseup', this._onMouseUp, this);
    },
    _onMouseMove: function (e) {
        e.target.setLatLng(e.latlng); // Use e.target to get the CircleMarker
    },
    _onMouseUp: function (e) {
        var leafletMap = this._map; // Get the map object
        leafletMap.dragging.enable(); // Re-enable map dragging
        leafletMap.off('mousemove', this._onMouseMove, this);
        leafletMap.off('mouseup', this._onMouseUp, this);
    }
});