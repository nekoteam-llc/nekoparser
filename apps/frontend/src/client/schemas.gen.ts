// This file is auto-generated by @hey-api/openapi-ts

export const $ConfigModel = {
	properties: {
		chatgpt_key: {
			type: 'string',
			title: 'Chatgpt Key'
		},
		model: {
			type: 'string',
			title: 'Model'
		},
		pages_concurrency: {
			type: 'integer',
			title: 'Pages Concurrency'
		},
		products_concurrency: {
			type: 'integer',
			title: 'Products Concurrency'
		},
		required: {
			items: {
				type: 'string'
			},
			type: 'array',
			title: 'Required'
		},
		not_reprocess: {
			items: {
				type: 'string'
			},
			type: 'array',
			title: 'Not Reprocess'
		},
		description_prompt: {
			type: 'string',
			title: 'Description Prompt'
		},
		keywords_prompt: {
			type: 'string',
			title: 'Keywords Prompt'
		},
		properties_prompt: {
			type: 'string',
			title: 'Properties Prompt'
		}
	},
	type: 'object',
	required: [
		'chatgpt_key',
		'model',
		'pages_concurrency',
		'products_concurrency',
		'required',
		'not_reprocess',
		'description_prompt',
		'keywords_prompt',
		'properties_prompt'
	],
	title: 'ConfigModel'
} as const;

export const $ConnectorSource = {
	properties: {
		id: {
			type: 'string',
			title: 'Id'
		},
		domain: {
			type: 'string',
			title: 'Domain'
		}
	},
	type: 'object',
	required: ['id', 'domain'],
	title: 'ConnectorSource'
} as const;

export const $ConnectorSourcesResponse = {
	properties: {
		sources: {
			items: {
				$ref: '#/components/schemas/ConnectorSource'
			},
			type: 'array',
			title: 'Sources'
		}
	},
	type: 'object',
	required: ['sources'],
	title: 'ConnectorSourcesResponse'
} as const;

export const $HTTPValidationError = {
	properties: {
		detail: {
			items: {
				$ref: '#/components/schemas/ValidationError'
			},
			type: 'array',
			title: 'Detail'
		}
	},
	type: 'object',
	title: 'HTTPValidationError'
} as const;

export const $MessageResponse = {
	properties: {
		message: {
			type: 'string',
			title: 'Message'
		}
	},
	type: 'object',
	required: ['message'],
	title: 'MessageResponse'
} as const;

export const $PingResponse = {
	properties: {
		message: {
			type: 'string',
			title: 'Message'
		}
	},
	type: 'object',
	required: ['message'],
	title: 'PingResponse'
} as const;

export const $PropertiesResponse = {
	properties: {
		properties: {
			items: {
				$ref: '#/components/schemas/Property'
			},
			type: 'array',
			title: 'Properties'
		}
	},
	type: 'object',
	required: ['properties'],
	title: 'PropertiesResponse'
} as const;

export const $Property = {
	properties: {
		name: {
			type: 'string',
			title: 'Name'
		},
		description: {
			type: 'string',
			title: 'Description'
		}
	},
	type: 'object',
	required: ['name', 'description'],
	title: 'Property'
} as const;

export const $PropertyInput = {
	properties: {
		property: {
			type: 'string',
			title: 'Property'
		},
		xpath: {
			type: 'string',
			title: 'Xpath'
		}
	},
	type: 'object',
	required: ['property', 'xpath'],
	title: 'PropertyInput'
} as const;

export const $RegExesInput = {
	properties: {
		product: {
			type: 'string',
			title: 'Product'
		},
		pagination: {
			type: 'string',
			title: 'Pagination'
		}
	},
	type: 'object',
	required: ['product', 'pagination'],
	title: 'RegExesInput'
} as const;

export const $ReprocessRequest = {
	properties: {
		products: {
			items: {
				type: 'string'
			},
			type: 'array',
			title: 'Products'
		}
	},
	type: 'object',
	required: ['products'],
	title: 'ReprocessRequest'
} as const;

export const $Source = {
	properties: {
		id: {
			type: 'string',
			title: 'Id'
		},
		url: {
			type: 'string',
			title: 'Url'
		},
		title: {
			type: 'string',
			title: 'Title'
		},
		description: {
			type: 'string',
			title: 'Description'
		},
		icon: {
			type: 'string',
			title: 'Icon'
		},
		state: {
			type: 'string',
			title: 'State'
		}
	},
	type: 'object',
	required: ['id', 'url', 'title', 'description', 'icon', 'state'],
	title: 'Source'
} as const;

export const $SourceCreateResponse = {
	properties: {
		id: {
			type: 'string',
			title: 'Id'
		}
	},
	type: 'object',
	required: ['id'],
	title: 'SourceCreateResponse'
} as const;

export const $SourceUpdateInput = {
	properties: {
		xpaths: {
			items: {
				$ref: '#/components/schemas/PropertyInput'
			},
			type: 'array',
			title: 'Xpaths'
		},
		regexes: {
			$ref: '#/components/schemas/RegExesInput'
		}
	},
	type: 'object',
	required: ['xpaths', 'regexes'],
	title: 'SourceUpdateInput'
} as const;

export const $SourceUpdateResponse = {
	properties: {
		message: {
			type: 'string',
			title: 'Message'
		}
	},
	type: 'object',
	required: ['message'],
	title: 'SourceUpdateResponse'
} as const;

export const $SourcesResponse = {
	properties: {
		sources: {
			items: {
				$ref: '#/components/schemas/Source'
			},
			type: 'array',
			title: 'Sources'
		}
	},
	type: 'object',
	required: ['sources'],
	title: 'SourcesResponse'
} as const;

export const $ValidationError = {
	properties: {
		loc: {
			items: {
				anyOf: [
					{
						type: 'string'
					},
					{
						type: 'integer'
					}
				]
			},
			type: 'array',
			title: 'Location'
		},
		msg: {
			type: 'string',
			title: 'Message'
		},
		type: {
			type: 'string',
			title: 'Error Type'
		}
	},
	type: 'object',
	required: ['loc', 'msg', 'type'],
	title: 'ValidationError'
} as const;
