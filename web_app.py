import flask
import geopandas as gpd
import folium

def style_function_solar(feature):
    return {
        'fillColor': "green",
        'color': "green",
        'weight': 2,
        'fillOpacity': 0.6
    }
    
def style_function_plant(feature):
    return {
        'fillColor': "red",
        'color': "red",
        'weight': 2,
        'fillOpacity': 1.0
    }
    
def style_function_com_solar(feature):
    return {
        'fillColor': "blue",
        'color': "blue",
        'weight': 2,
        'fillOpacity': 1.0
    }

class CommunityMappingApp:
    def __init__(self):
        self.gdf_power_plants, self.gdf_solar_panels, self.gdf_com_solar_panels = self.get_geodataframe()        
        self.app = flask.Flask(__name__)
        self.routes()

    def get_geodataframe(self):
        gdf_power_plants = gpd.read_file(r"C:\Users\josep\Desktop\Code\Local Projects\InsightsNow\Data\Power_Plant_Parcels_of_New_Jersey.geojson")
        gdf_solar_panels = gpd.read_file(r"C:\Users\josep\Desktop\Code\Local Projects\InsightsNow\Data\Public_Solar_Facilities_of_New_Jersey.geojson")
        gdf_solar_panels["STATUSDATE"] = gdf_solar_panels["STATUSDATE"].astype(str).apply(lambda x: x[0:4])
        print(gdf_solar_panels["STATUSDATE"])
        gdf_com_solar_panels = gpd.read_file(r"C:\Users\josep\Desktop\Code\Local Projects\InsightsNow\Data\New_Jersey_Community_Solar_PV_Projects.geojson")
        return gdf_power_plants, gdf_solar_panels, gdf_com_solar_panels

    def create_map(self, gdf_power_plants, gdf_solar_panels, gdf_com_solar_panels):    
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
        folium.GeoJson(gdf_power_plants, name='Power Plants', style_function=style_function_plant).add_to(map)
        folium.GeoJson(gdf_solar_panels, name='Public Solar Panels', style_function=style_function_solar, marker=folium.Circle(radius=10, tooltip="Public Solar Infrastructure")).add_to(map)
        folium.GeoJson(gdf_com_solar_panels, name="Community Solar Panels", style_function=style_function_com_solar, marker=folium.Circle(radius=10, tooltip="Community Solar Project")).add_to(map)
        
        folium.LayerControl().add_to(map)
        
        legend_html = """
     <div style="position: fixed; 
                 bottom: 60px; left: 50px; width: 200px; height: 130px; 
                 border:1px solid grey; z-index:9999; font-size:12px;
                 background-color:white; padding: 8px;">
       <h4 style="margin: 0;">Legend</h4>
       <p style="margin: 0;"><i class="fa fa-map-marker fa-2x" style="color: red"></i> Nonrenewable Energy Source</p>
       <p style="margin: 0;"><i class="fa fa-map-marker fa-2x" style="color: blue"></i> Community Solar Project</p>
       <p style="margin: 0;"><i class="fa fa-map-marker fa-2x" style="color: green"></i> Public Solar Infrastructure</p>
     </div>
     """

        map.get_root().html.add_child(folium.Element(legend_html))
        
        map.save(r"templates/map.html")
        with open(r"templates/map.html", "r") as map_file:
            map_html = map_file.read()
        return map_html

    def routes(self):
        @self.app.route("/")
        def home():
            year = flask.request.args.get("year", 2024)
            gdf_solar_panels = self.filter_year(int(year))
            map_html = self.create_map(self.gdf_power_plants, gdf_solar_panels, self.gdf_com_solar_panels)
            
            return flask.render_template(r"index.html", map_html=map_html, year=year)

        @self.app.route('/update_map')
        def update_map():
            # Updates based on filter (currently only solar_panels)
            year = flask.request.args.get("year", 2024)
            gdf_solar_panels = self.filter_year(int(year))
            map_html = self.create_map(self.gdf_power_plants, gdf_solar_panels, self.gdf_com_solar_panels)
            return map_html

    def filter_year(self, year):
        # Filters the solar panel data to selected year
        filtered = self.gdf_solar_panels[self.gdf_solar_panels["STATUSDATE"].apply(lambda x: int(x) if x[0] == 0 else 0) <= year]
        # Filters for other data TBD
        return filtered


if __name__ == '__main__':
    base = CommunityMappingApp()
    base.app.run(debug=True)

