// File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

import { APIResource } from '../resource';
import * as Core from '../core';

export class Text extends APIResource {
  /**
   * Tone Mark
   */
  toneMark(body: TextToneMarkParams, options?: Core.RequestOptions): Core.APIPromise<TextToneMarkResponse> {
    return this._client.post('/v1/diacritics', { body, ...options });
  }

  /**
   * Translate
   */
  translate(
    body: TextTranslateParams,
    options?: Core.RequestOptions,
  ): Core.APIPromise<TextTranslateResponse> {
    return this._client.post('/v1/translate', { body, ...options });
  }
}

export interface TextToneMarkResponse {
  request_id: string;

  text?: string;
}

export interface TextTranslateResponse {
  request_id: string;

  text?: string;
}

export interface TextToneMarkParams {
  language: 'yo' | 'en' | 'ha' | 'ig' | 'am';

  text: string;
}

export interface TextTranslateParams {
  source: 'yo' | 'en' | 'ha' | 'ig' | 'am';

  target: 'yo' | 'en' | 'ha' | 'ig' | 'am';

  text: string;
}

export declare namespace Text {
  export {
    type TextToneMarkResponse as TextToneMarkResponse,
    type TextTranslateResponse as TextTranslateResponse,
    type TextToneMarkParams as TextToneMarkParams,
    type TextTranslateParams as TextTranslateParams,
  };
}
