from odoo import _, api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'


    rayl_community_user_exists_url = fields.Text('Rayl Community User Exists Url')
    rayl_community_user_update_url = fields.Text('Rayl Community User Update Url')
    rayl_community_admin_username = fields.Text('Rayl Community Admin Username')
    rayl_community_admin_password = fields.Text('Rayl Community Admin Password')
    rayl_community_user_url = fields.Text('Rayl Community User URl')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        res.update(
            rayl_community_user_exists_url=self.env['ir.config_parameter'].sudo().get_param(
                'rayl_community.rayl_community_user_exists_url'),
            rayl_community_user_update_url=self.env['ir.config_parameter'].sudo().get_param(
                'rayl_community.rayl_community_user_update_url'),
            rayl_community_admin_username=self.env['ir.config_parameter'].sudo().get_param(
                'rayl_community.rayl_community_admin_username'),
            rayl_community_admin_password=self.env['ir.config_parameter'].sudo().get_param(
                'rayl_community.rayl_community_admin_password'),
        )
        return res

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        param = self.env['ir.config_parameter'].sudo()
        rayl_community_user_exists_url = self.rayl_community_user_exists_url and self.rayl_community_user_exists_url or False
        rayl_community_user_update_url = self.rayl_community_user_update_url and self.rayl_community_user_update_url or False
        rayl_community_admin_username = self.rayl_community_admin_username and self.rayl_community_admin_username or False
        rayl_community_admin_password = self.rayl_community_admin_password and self.rayl_community_admin_password or False

        param.set_param('rayl_community.rayl_community_user_exists_url', rayl_community_user_exists_url)
        param.set_param('rayl_community.rayl_community_user_update_url', rayl_community_user_update_url)
        param.set_param('rayl_community.rayl_community_admin_username', rayl_community_admin_username)
        param.set_param('rayl_community.rayl_community_admin_password', rayl_community_admin_password)
