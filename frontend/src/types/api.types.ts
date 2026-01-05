/**
 * Generic paginated response
 */
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

/**
 * Generic API error response
 */
export interface APIError {
  detail: string;
  status_code?: number;
}

/**
 * Generic success message response
 */
export interface MessageResponse {
  message: string;
}

/**
 * Query params for paginated requests
 */
export interface PaginationParams {
  page?: number;
  per_page?: number;
}

/**
 * Query params for search
 */
export interface SearchParams extends PaginationParams {
  search?: string;
}
