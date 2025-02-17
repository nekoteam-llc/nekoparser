// This file is auto-generated by @hey-api/openapi-ts

export type Body_upload_excel_file_api_v1_sources_excel_post = {
	file: Blob | File;
};

export type ConfigModel = {
	chatgpt_key: string;
	model: string;
	pages_concurrency: number;
	products_concurrency: number;
	required: Array<string>;
	not_reprocess: Array<string>;
	description_prompt: string;
	keywords_prompt: string;
	properties_prompt: string;
};

export type ConnectorSource = {
	id: string;
	domain: string;
};

export type ConnectorSourcesResponse = {
	sources: Array<ConnectorSource>;
};

export type ExcelSourceModel = {
	id: string;
	filename: string;
	state: string;
	type: string;
	url: string;
};

export type HTTPValidationError = {
	detail?: Array<ValidationError>;
};

export type MessageResponse = {
	message: string;
};

export type PingResponse = {
	message: string;
};

export type PropertiesResponse = {
	properties: Array<Property>;
};

export type Property = {
	name: string;
	description: string;
};

export type PropertyInput = {
	property: string;
	xpath: string;
};

export type RegExesInput = {
	product: string;
	pagination: string;
};

export type ReprocessRequest = {
	products: Array<string>;
};

export type SourceCreateResponse = {
	id: string;
};

export type SourceUpdateInput = {
	xpaths: Array<PropertyInput>;
	regexes: RegExesInput;
};

export type SourceUpdateResponse = {
	message: string;
};

export type SourcesResponse = {
	sources: Array<WebsiteSourceModel>;
};

export type UpdateSourceRequest = {
	name: string | null;
	description: string | null;
};

export type ValidationError = {
	loc: Array<string | number>;
	msg: string;
	type: string;
};

export type WebsiteSourceModel = {
	id: string;
	url: string;
	title: string;
	description: string;
	icon: string;
	state: string;
	type: string;
};

export type GetConfigApiV1ConfigGetResponse = ConfigModel;

export type UpdateConfigApiV1ConfigPutData = {
	requestBody: ConfigModel;
};

export type UpdateConfigApiV1ConfigPutResponse = ConfigModel;

export type GetActiveSourcesApiV1ConnectorSourcesGetResponse = ConnectorSourcesResponse;

export type GetPropertiesApiV1ConnectorPropertiesGetResponse = PropertiesResponse;

export type UpdateSourceXpathsApiV1ConnectorSourcesSourceIdPostData = {
	requestBody: SourceUpdateInput;
	sourceId: string;
};

export type UpdateSourceXpathsApiV1ConnectorSourcesSourceIdPostResponse = SourceUpdateResponse;

export type PingApiV1PingGetResponse = PingResponse;

export type GetSourcesApiV1SourcesGetResponse = SourcesResponse;

export type CreateSourceApiV1SourcesPostData = {
	url: string;
};

export type CreateSourceApiV1SourcesPostResponse = SourceCreateResponse;

export type GetSourceApiV1SourcesSourceIdGetData = {
	sourceId: string;
};

export type GetSourceApiV1SourcesSourceIdGetResponse = WebsiteSourceModel | ExcelSourceModel;

export type DeleteSourceApiV1SourcesSourceIdDeleteData = {
	sourceId: string;
};

export type DeleteSourceApiV1SourcesSourceIdDeleteResponse = MessageResponse;

export type UpdateSourceApiV1SourcesSourceIdPutData = {
	requestBody: UpdateSourceRequest;
	sourceId: string;
};

export type UpdateSourceApiV1SourcesSourceIdPutResponse = MessageResponse;

export type ReloadSourcesApiV1SourcesReloadPostResponse = MessageResponse;

export type ReprocessProductsApiV1SourcesReprocessPostData = {
	requestBody: ReprocessRequest;
};

export type ReprocessProductsApiV1SourcesReprocessPostResponse = MessageResponse;

export type UploadExcelFileApiV1SourcesExcelPostData = {
	formData: Body_upload_excel_file_api_v1_sources_excel_post;
};

export type UploadExcelFileApiV1SourcesExcelPostResponse = SourceCreateResponse;

export type $OpenApiTs = {
	'/api/v1/config/': {
		get: {
			res: {
				/**
				 * Successful Response
				 */
				200: ConfigModel;
			};
		};
		put: {
			req: UpdateConfigApiV1ConfigPutData;
			res: {
				/**
				 * Successful Response
				 */
				200: ConfigModel;
				/**
				 * Validation Error
				 */
				422: HTTPValidationError;
			};
		};
	};
	'/api/v1/connector/sources': {
		get: {
			res: {
				/**
				 * Successful Response
				 */
				200: ConnectorSourcesResponse;
			};
		};
	};
	'/api/v1/connector/properties': {
		get: {
			res: {
				/**
				 * Successful Response
				 */
				200: PropertiesResponse;
			};
		};
	};
	'/api/v1/connector/sources/{source_id}': {
		post: {
			req: UpdateSourceXpathsApiV1ConnectorSourcesSourceIdPostData;
			res: {
				/**
				 * Successful Response
				 */
				200: SourceUpdateResponse;
				/**
				 * Validation Error
				 */
				422: HTTPValidationError;
			};
		};
	};
	'/api/v1/ping/': {
		get: {
			res: {
				/**
				 * Successful Response
				 */
				200: PingResponse;
			};
		};
	};
	'/api/v1/sources/': {
		get: {
			res: {
				/**
				 * Successful Response
				 */
				200: SourcesResponse;
			};
		};
		post: {
			req: CreateSourceApiV1SourcesPostData;
			res: {
				/**
				 * Successful Response
				 */
				200: SourceCreateResponse;
				/**
				 * Validation Error
				 */
				422: HTTPValidationError;
			};
		};
	};
	'/api/v1/sources/{source_id}': {
		get: {
			req: GetSourceApiV1SourcesSourceIdGetData;
			res: {
				/**
				 * Successful Response
				 */
				200: WebsiteSourceModel | ExcelSourceModel;
				/**
				 * Validation Error
				 */
				422: HTTPValidationError;
			};
		};
		delete: {
			req: DeleteSourceApiV1SourcesSourceIdDeleteData;
			res: {
				/**
				 * Successful Response
				 */
				200: MessageResponse;
				/**
				 * Validation Error
				 */
				422: HTTPValidationError;
			};
		};
		put: {
			req: UpdateSourceApiV1SourcesSourceIdPutData;
			res: {
				/**
				 * Successful Response
				 */
				200: MessageResponse;
				/**
				 * Validation Error
				 */
				422: HTTPValidationError;
			};
		};
	};
	'/api/v1/sources/reload': {
		post: {
			res: {
				/**
				 * Successful Response
				 */
				200: MessageResponse;
			};
		};
	};
	'/api/v1/sources/reprocess': {
		post: {
			req: ReprocessProductsApiV1SourcesReprocessPostData;
			res: {
				/**
				 * Successful Response
				 */
				200: MessageResponse;
				/**
				 * Validation Error
				 */
				422: HTTPValidationError;
			};
		};
	};
	'/api/v1/sources/excel': {
		post: {
			req: UploadExcelFileApiV1SourcesExcelPostData;
			res: {
				/**
				 * Successful Response
				 */
				200: SourceCreateResponse;
				/**
				 * Validation Error
				 */
				422: HTTPValidationError;
			};
		};
	};
};
