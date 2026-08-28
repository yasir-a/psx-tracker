export interface APIErrorResponse {
  error: {
    code: string;
    message: string;
    details: Record<string, unknown>;
  };
}