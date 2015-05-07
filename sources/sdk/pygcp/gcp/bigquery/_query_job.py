# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#  http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Implements BigQuery query job functionality."""

from ._job import Job as _Job


class QueryJob(_Job):
  """ Represents a BigQuery Query Job.
  """

  def __init__(self, api, job_id, table_name, sql):
    super(QueryJob, self).__init__(api, job_id)
    self._sql = sql
    self._table = _QueryResultsTable(api, table_name, self, is_temporary=True)

  def wait(self, timeout=None):
    """ Wait for the job to complete, or a timeout to happen.

      This is more efficient than the version in the base Job class, in that we can
      use a call that blocks for the poll duration rather than a sleep. That means we
      shouldn't block unnecessarily long and can also poll less.

    Args:
      timeout: how long to wait (in seconds) before giving up; default None which means no timeout.

    Returns:
      The Job
    """
    poll = 30
    while not self._is_complete:
      query_result = self._api.jobs_query_results(self._job_id,
                                                  project_id=self._table.name.project_id,
                                                  page_size=0,
                                                  timeout=poll * 1000)
      if query_result['jobComplete']:
        break

      if timeout is not None:
        timeout -= poll
        if timeout <= 0:
          break

    self._refresh_state()
    return self

  @property
  def results(self):
    """ Get the table used for the results of the query. If the query is incomplete, this blocks.

    Raises:
      Exception if we timed out waiting for results or the query failed.
    """
    self.wait()
    if self.failed:
      raise Exception('Query failed: %s' % str(self.errors))
    return self._table

  @property
  def sql(self):
    return self._sql

from ._query_results_table import QueryResultsTable as _QueryResultsTable
