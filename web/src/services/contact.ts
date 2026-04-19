/**
 * 联系人服务
 * 联系人列表：GET /api/contacts/ → [Contact]
 */
import { apiClient, handleApiResponse } from './api';
import type { Contact } from '@/types';

/**
 * 后端联系人响应数据结构（下划线命名）
 */
export interface BackendContact {
  id: number;
  name: string;
  phone: string;
  relation?: string;
  is_primary: boolean;
  created_at?: string;
  updated_at?: string;
}

/**
 * 转换后端联系人数据为前端格式
 * @param c 后端联系人数据（下划线命名）
 * @returns 前端联系人数据（驼峰命名）
 */
function convertBackendContact(c: BackendContact): Contact {
  return {
    id: String(c.id),
    userId: undefined,
    name: c.name,
    phone: c.phone,
    relationship: c.relation,
    isEmergency: c.is_primary,
    createdAt: c.created_at || new Date().toISOString(),
    updatedAt: c.updated_at || c.created_at || new Date().toISOString(),
  };
}

/**
 * 创建联系人请求参数
 */
export interface CreateContactParams {
  name: string;
  phone: string;
  relation?: string;
  is_primary?: boolean;
}

/**
 * 更新联系人请求参数
 */
export interface UpdateContactParams {
  name?: string;
  phone?: string;
  relation?: string;
  is_primary?: boolean;
}

/**
 * 获取联系人列表
 * @returns 联系人列表
 * @throws ApiError 请求失败时抛出错误
 */
export async function getContacts(): Promise<Contact[]> {
  const response = await apiClient.get('/contacts/');
  const contacts = handleApiResponse<BackendContact[]>(response);
  return contacts.map(convertBackendContact);
}

/**
 * 获取单个联系人详情
 * @param contactId 联系人ID
 * @returns 联系人详情
 * @throws ApiError 请求失败时抛出错误
 */
export async function getContact(contactId: string): Promise<Contact> {
  const response = await apiClient.get(`/contacts/${contactId}`);
  const c = handleApiResponse<BackendContact>(response);
  return convertBackendContact(c);
}

/**
 * 创建联系人
 * @param params 联系人参数
 * @returns 创建的联系人信息
 * @throws ApiError 请求失败时抛出错误
 */
export async function createContact(params: CreateContactParams): Promise<Contact> {
  const requestData = {
    name: params.name,
    phone: params.phone,
    relation: params.relation || '',
    is_primary: params.is_primary ?? false,
  };

  const response = await apiClient.post('/contacts/', requestData);
  const c = handleApiResponse<BackendContact>(response);
  return convertBackendContact(c);
}

/**
 * 更新联系人
 * @param contactId 联系人ID
 * @param params 更新参数
 * @returns 更新后的联系人信息
 * @throws ApiError 请求失败时抛出错误
 */
export async function updateContact(contactId: string, params: UpdateContactParams): Promise<Contact> {
  const requestData: Record<string, string | boolean> = {};

  if (params.name !== undefined) requestData.name = params.name;
  if (params.phone !== undefined) requestData.phone = params.phone;
  if (params.relation !== undefined) requestData.relation = params.relation;
  if (params.is_primary !== undefined) requestData.is_primary = params.is_primary;

  const response = await apiClient.put(`/contacts/${contactId}`, requestData);
  const c = handleApiResponse<BackendContact>(response);
  return convertBackendContact(c);
}

/**
 * 删除联系人
 * @param contactId 联系人ID
 * @throws ApiError 请求失败时抛出错误
 */
export async function deleteContact(contactId: string): Promise<void> {
  await apiClient.delete(`/contacts/${contactId}`);
}
