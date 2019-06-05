from tethys_sdk.base import TethysAppBase, url_map_maker


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
        )

        return url_maps
