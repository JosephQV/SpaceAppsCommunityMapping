import flask
import geopandas as gpd
import folium


class CommunityMappingApp:
    def __init__(self):
        self.gdf_power_plants, self.gdf_solar_panels, self.gdf_other = self.get_geodataframe()        
        self.app = flask.Flask(__name__)
        self.routes()

    def get_geodataframe(self):
        gdf_power_plants = gpd.read_file(r"C:\Users\josep\Desktop\Code\Local Projects\InsightsNow\Data\Power_Plant_Parcels_of_New_Jersey.geojson")
        gdf_solar_panels = None
        gdf_other = None
        return gdf_power_plants, gdf_solar_panels, gdf_other

    def create_map(self, gdf_power_plants, gdf_solar_panels, gdf_emissivity):    
        map = folium.Map(
            max_bounds=True,
            location=[40, -74],
            zoom_start=8,
            min_lat=38,
            max_lat=42,
            min_lon=-70,
            max_lon=-78,
            min_zoom=7
        )
        folium.GeoJson(gdf_power_plants, name='Power Plants').add_to(map)
        # TBD folium.GeoJson(gdf_solar_panels, name='Solar Panels').add_to(map)
        
        folium.LayerControl().add_to(map)
        
        map.save(r"templates/map.html")
        with open(r"templates/map.html", "r") as map_file:
            map_html = map_file.read()
        return map_html

    def routes(self):
        @self.app.route("/")
        def home():
            year = flask.request.args.get("year", 2024)
            map_html = self.create_map(self.gdf_power_plants, self.gdf_solar_panels, self.gdf_other)
            
            return flask.render_template(r"index.html", map_html=map_html, year=year)

        @self.app.route('/update_map')
        def update_map():
            # Updates based on filter (currently only solar_panels)
            year = flask.request.args.get("year", 2024)
            gdf_solar_panels = self.filter_year(int(year))
            map_html = self.create_map(self.gdf_power_plants, gdf_solar_panels, self.gdf_other)
            return map_html

    def filter_year(self, year):
        # Filters the solar panel data to selected year
        filtered = self.gdf_solar_panels[self.gdf_solar_panels["Year"] == year]
        # Filters for other data TBD
        return filtered


if __name__ == '__main__':
    base = CommunityMappingApp()
    base.app.run(debug=True)

