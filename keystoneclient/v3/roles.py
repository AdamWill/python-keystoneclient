# Copyright 2011 OpenStack Foundation
# Copyright 2011 Nebula, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

from positional import positional

from keystoneclient import base
from keystoneclient import exceptions
from keystoneclient.i18n import _


class Role(base.Resource):
    """Represents an Identity role.

    Attributes:
        * id: a uuid that identifies the role
        * name: user-facing identifier
        * domain: optional domain for the role

    """

    pass


class InferenceRule(base.Resource):
    """Represents an Rule that states one ROle implies another.

    Attributes:
        * prior_role: this role implies the other
        * implied_role: this role is implied by the other

    """

    pass


class RoleManager(base.CrudManager):
    """Manager class for manipulating Identity roles."""

    resource_class = Role
    collection_key = 'roles'
    key = 'role'

    def _role_grants_base_url(self, user, group, domain, project,
                              use_inherit_extension):
        # When called, we have already checked that only one of user & group
        # and one of domain & project have been specified
        params = {}

        if project:
            params['project_id'] = base.getid(project)
            base_url = '/projects/%(project_id)s'
        elif domain:
            params['domain_id'] = base.getid(domain)
            base_url = '/domains/%(domain_id)s'

        if use_inherit_extension:
            base_url = '/OS-INHERIT' + base_url

        if user:
            params['user_id'] = base.getid(user)
            base_url += '/users/%(user_id)s'
        elif group:
            params['group_id'] = base.getid(group)
            base_url += '/groups/%(group_id)s'

        return base_url % params

    def _require_domain_xor_project(self, domain, project):
        if domain and project:
            msg = _('Specify either a domain or project, not both')
            raise exceptions.ValidationError(msg)
        elif not (domain or project):
            msg = _('Must specify either a domain or project')
            raise exceptions.ValidationError(msg)

    def _require_user_xor_group(self, user, group):
        if user and group:
            msg = _('Specify either a user or group, not both')
            raise exceptions.ValidationError(msg)
        elif not (user or group):
            msg = _('Must specify either a user or group')
            raise exceptions.ValidationError(msg)

    @positional(1, enforcement=positional.WARN)
    def create(self, name, domain=None, **kwargs):
        """Create a role.

        :param str name: the name of the role.
        :param domain: the domain of the role. If a value is passed it is a
                       domain-scoped role, otherwise it's a global role.
        :type domain: str or :class:`keystoneclient.v3.domains.Domain`
        :param kwargs: any other attribute provided will be passed to the
                       server.

        :returns: the created role returned from server.
        :rtype: :class:`keystoneclient.v3.roles.Role`

        """
        domain_id = None
        if domain:
            domain_id = base.getid(domain)

        return super(RoleManager, self).create(
            name=name,
            domain_id=domain_id,
            **kwargs)

    def _implied_role_url_tail(self, prior_role, implied_role):
        base_url = ('/%(prior_role_id)s/implies/%(implied_role_id)s' %
                    {'prior_role_id': base.getid(prior_role),
                     'implied_role_id': base.getid(implied_role)})
        return base_url

    def create_implied(self, prior_role, implied_role, **kwargs):
        """Create an inference rule.

        :param prior_role: the role which implies ``implied_role``.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param implied_role: the role which is implied by ``prior_role``.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param kwargs: any other attribute provided will be passed to the
                       server.

        """
        url_tail = self._implied_role_url_tail(prior_role, implied_role)
        self.client.put("/roles" + url_tail, **kwargs)

    def delete_implied(self, prior_role, implied_role, **kwargs):
        """Delete an inference rule.

        :param prior_role: the role which implies ``implied_role``.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param implied_role: the role which is implied by ``prior_role``.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param kwargs: any other attribute provided will be passed to the
                       server.

        :returns: Response object with 204 status.
        :rtype: :class:`requests.models.Response`

        """
        url_tail = self._implied_role_url_tail(prior_role, implied_role)
        return super(RoleManager, self).delete(tail=url_tail, **kwargs)

    def get_implied(self, prior_role, implied_role, **kwargs):
        """Retrieve an inference rule.

        :param prior_role: the role which implies ``implied_role``.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param implied_role: the role which is implied by ``prior_role``.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param kwargs: any other attribute provided will be passed to the
                       server.

        :returns: the specified role inference returned from server.
        :rtype: :class:`keystoneclient.v3.roles.InferenceRule`

        """
        url_tail = self._implied_role_url_tail(prior_role, implied_role)
        return super(RoleManager, self).get(tail=url_tail, **kwargs)

    def check_implied(self, prior_role, implied_role, **kwargs):
        """Check if an inference rule exists.

        :param prior_role: the role which implies ``implied_role``.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param implied_role: the role which is implied by ``prior_role``.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param kwargs: any other attribute provided will be passed to the
                       server.

        :returns: response object with 200 status returned from server.
        :rtype: :class:`requests.models.Response`

        """
        url_tail = self._implied_role_url_tail(prior_role, implied_role)
        return super(RoleManager, self).head(tail=url_tail, **kwargs)

    def list_role_inferences(self, **kwargs):
        """List role inferences.

        :param kwargs: attributes provided will be passed to the server.

        :returns: a list of roles inferences.
        :rtype: list of :class:`keystoneclient.v3.roles.InferenceRule`

        """
        resp, body = self.client.get('/role_inferences/', **kwargs)
        obj_class = InferenceRule
        return [obj_class(self, res, loaded=True)
                for res in body['role_inferences']]

    def get(self, role):
        """Retrieve a role.

        :param role: the role to be retrieved from the server.
        :type role: str or :class:`keystoneclient.v3.roles.Role`

        :returns: the specified role returned from server.
        :rtype: :class:`keystoneclient.v3.roles.Role`

        """
        return super(RoleManager, self).get(role_id=base.getid(role))

    @positional(enforcement=positional.WARN)
    def list(self, user=None, group=None, domain=None,
             project=None, os_inherit_extension_inherited=False, **kwargs):
        """List roles and role grants.

        :param user: filter in role grants for the specified user on a
                     resource. Domain or project must be specified.
                     User and group are mutually exclusive.
        :type user: str or :class:`keystoneclient.v3.users.User`
        :param group: filter in role grants for the specified group on a
                      resource. Domain or project must be specified.
                      User and group are mutually exclusive.
        :type group: str or :class:`keystoneclient.v3.groups.Group`
        :param domain: filter in role grants on the specified domain. Either
                       user or group must be specified. Project and domain
                       are mutually exclusive.
        :type domain: str or :class:`keystoneclient.v3.domains.Domain`
        :param project: filter in role grants on the specified project. Either
                       user or group must be specified. Project and domain
                       are mutually exclusive.
        :type project: str or :class:`keystoneclient.v3.projects.Project`
        :param bool os_inherit_extension_inherited: OS-INHERIT will be used.
                                                    It provides the ability for
                                                    projects to inherit role
                                                    assignments from their
                                                    domains or from parent
                                                    projects in the hierarchy.
        :param kwargs: any other attribute provided will filter roles on.

        :returns: a list of roles.
        :rtype: list of :class:`keystoneclient.v3.roles.Role`

        """
        if os_inherit_extension_inherited:
            kwargs['tail'] = '/inherited_to_projects'
        if user or group:
            self._require_user_xor_group(user, group)
            self._require_domain_xor_project(domain, project)

            base_url = self._role_grants_base_url(
                user, group, domain, project, os_inherit_extension_inherited)
            return super(RoleManager, self).list(base_url=base_url,
                                                 **kwargs)

        return super(RoleManager, self).list(**kwargs)

    @positional(enforcement=positional.WARN)
    def update(self, role, name=None, **kwargs):
        """Update a role.

        :param role: the role to be updated on the server.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param str name: the new name of the role.
        :param kwargs: any other attribute provided will be passed to server.

        :returns: the updated role returned from server.
        :rtype: :class:`keystoneclient.v3.roles.Role`

        """
        return super(RoleManager, self).update(
            role_id=base.getid(role),
            name=name,
            **kwargs)

    def delete(self, role):
        """Delete a role.

        When a role is deleted all the role inferences that have deleted role
        as prior role will be deleted as well.

        :param role: the role to be deleted on the server.
        :type role: str or :class:`keystoneclient.v3.roles.Role`

        :returns: Response object with 204 status.
        :rtype: :class:`requests.models.Response`

        """
        return super(RoleManager, self).delete(
            role_id=base.getid(role))

    @positional(enforcement=positional.WARN)
    def grant(self, role, user=None, group=None, domain=None, project=None,
              os_inherit_extension_inherited=False, **kwargs):
        """Grant a role to a user or group on a domain or project.

        :param role: the role to be granted on the server.
        :type role: str or :class:`keystoneclient.v3.roles.Role`
        :param user: the specified user to have the role granted on a resource.
                     Domain or project must be specified. User and group are
                     mutually exclusive.
        :type user: str or :class:`keystoneclient.v3.users.User`
        :param group: the specified group to have the role granted on a
                      resource. Domain or project must be specified.
                      User and group are mutually exclusive.
        :type group: str or :class:`keystoneclient.v3.groups.Group`
        :param domain: the domain in which the role will be granted. Either
                       user or group must be specified. Project and domain
                       are mutually exclusive.
        :type domain: str or :class:`keystoneclient.v3.domains.Domain`
        :param project: the project in which the role will be granted. Either
                       user or group must be specified. Project and domain
                       are mutually exclusive.
        :type project: str or :class:`keystoneclient.v3.projects.Project`
        :param bool os_inherit_extension_inherited: OS-INHERIT will be used.
                                                    It provides the ability for
                                                    projects to inherit role
                                                    assignments from their
                                                    domains or from parent
                                                    projects in the hierarchy.
        :param kwargs: any other attribute provided will be passed to server.

        :returns: the granted role returned from server.
        :rtype: :class:`keystoneclient.v3.roles.Role`

        """
        self._require_domain_xor_project(domain, project)
        self._require_user_xor_group(user, group)

        if os_inherit_extension_inherited:
            kwargs['tail'] = '/inherited_to_projects'

        base_url = self._role_grants_base_url(
            user, group, domain, project, os_inherit_extension_inherited)
        return super(RoleManager, self).put(base_url=base_url,
                                            role_id=base.getid(role),
                                            **kwargs)

    @positional(enforcement=positional.WARN)
    def check(self, role, user=None, group=None, domain=None, project=None,
              os_inherit_extension_inherited=False, **kwargs):
        """Check if a user or group has a role on a domain or project.

        :param user: check for role grants for the specified user on a
                     resource. Domain or project must be specified.
                     User and group are mutually exclusive.
        :type user: str or :class:`keystoneclient.v3.users.User`
        :param group: check for role grants for the specified group on a
                      resource. Domain or project must be specified.
                      User and group are mutually exclusive.
        :type group: str or :class:`keystoneclient.v3.groups.Group`
        :param domain: check for role grants on the specified domain. Either
                       user or group must be specified. Project and domain
                       are mutually exclusive.
        :type domain: str or :class:`keystoneclient.v3.domains.Domain`
        :param project: check for role grants on the specified project. Either
                       user or group must be specified. Project and domain
                       are mutually exclusive.
        :type project: str or :class:`keystoneclient.v3.projects.Project`
        :param bool os_inherit_extension_inherited: OS-INHERIT will be used.
                                                    It provides the ability for
                                                    projects to inherit role
                                                    assignments from their
                                                    domains or from parent
                                                    projects in the hierarchy.
        :param kwargs: any other attribute provided will be passed to server.

        :returns: the specified role returned from server if it exists.
        :rtype: :class:`keystoneclient.v3.roles.Role`

        :returns: Response object with 204 status if specified role
                  doesn't exist.
        :rtype: :class:`requests.models.Response`

        """
        self._require_domain_xor_project(domain, project)
        self._require_user_xor_group(user, group)

        if os_inherit_extension_inherited:
            kwargs['tail'] = '/inherited_to_projects'

        base_url = self._role_grants_base_url(
            user, group, domain, project, os_inherit_extension_inherited)
        return super(RoleManager, self).head(
            base_url=base_url,
            role_id=base.getid(role),
            os_inherit_extension_inherited=os_inherit_extension_inherited,
            **kwargs)

    @positional(enforcement=positional.WARN)
    def revoke(self, role, user=None, group=None, domain=None, project=None,
               os_inherit_extension_inherited=False, **kwargs):
        """Revoke a role from a user or group on a domain or project.

        :param user: revoke role grants for the specified user on a
                     resource. Domain or project must be specified.
                     User and group are mutually exclusive.
        :type user: str or :class:`keystoneclient.v3.users.User`
        :param group: revoke role grants for the specified group on a
                      resource. Domain or project must be specified.
                      User and group are mutually exclusive.
        :type group: str or :class:`keystoneclient.v3.groups.Group`
        :param domain: revoke role grants on the specified domain. Either
                       user or group must be specified. Project and domain
                       are mutually exclusive.
        :type domain: str or :class:`keystoneclient.v3.domains.Domain`
        :param project: revoke role grants on the specified project. Either
                       user or group must be specified. Project and domain
                       are mutually exclusive.
        :type project: str or :class:`keystoneclient.v3.projects.Project`
        :param bool os_inherit_extension_inherited: OS-INHERIT will be used.
                                                    It provides the ability for
                                                    projects to inherit role
                                                    assignments from their
                                                    domains or from parent
                                                    projects in the hierarchy.
        :param kwargs: any other attribute provided will be passed to server.

        :returns: the revoked role returned from server.
        :rtype: list of :class:`keystoneclient.v3.roles.Role`

        """
        self._require_domain_xor_project(domain, project)
        self._require_user_xor_group(user, group)

        if os_inherit_extension_inherited:
            kwargs['tail'] = '/inherited_to_projects'

        base_url = self._role_grants_base_url(
            user, group, domain, project, os_inherit_extension_inherited)
        return super(RoleManager, self).delete(
            base_url=base_url,
            role_id=base.getid(role),
            os_inherit_extension_inherited=os_inherit_extension_inherited,
            **kwargs)
