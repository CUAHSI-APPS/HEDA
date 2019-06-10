from tethys_sdk.base import TethysAppBase, url_map_maker
from tethys_sdk.app_settings import CustomSetting

class Heda(TethysAppBase):
    """
    Tethys app class for HEDA.
    """

    name = 'HEDA'
    index = 'heda:home'
    icon = 'heda/images/icon.gif'
    package = 'heda'
    root_url = 'heda'
    color = '#f39c12'
    description = 'Hydrological environmental data analysis'
    tags = '&quot;#27AE60&quot;'
    enable_feedback = False
    feedback_emails = []

    def url_maps(self):
        """
        Add controllers
        """
        UrlMap = url_map_maker(self.root_url)

        url_maps = (
            UrlMap(
                name='home',
                url='heda',
                controller='heda.controllers.home'
            ),
            
        UrlMap(
                name='add_data',
                url='heda/data/add',
                controller='heda.controllers.add_data'
            ),
            
        )

        return url_maps
        
        
    def custom_settings(self):
        """
        Example custom_settings method.
        """
        custom_settings = (
            CustomSetting(
                name='max size',
                type=CustomSetting.TYPE_INTEGER,
                description='Maximum number of size in MB for data analysis - test feature',
                required=False
            ),
        )
        return custom_settings
