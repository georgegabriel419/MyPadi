// File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import type { Spitch } from './index';

export abstract class APIResource {
  protected _client: Spitch;

  constructor(client: Spitch) {
    this._client = client;
  }
}
