/**
 * 联系人管理页面
 */
import { useEffect, useState } from 'react';
import {
  User,
  Phone,
  Trash2,
  Edit2,
  Plus,
  X,
  AlertCircle,
} from 'lucide-react';
import { getContacts, createContact, updateContact, deleteContact } from '@/services/contact';
import type { Contact } from '@/types';

export default function ContactsPage() {
  const [contacts, setContacts] = useState<Contact[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingContact, setEditingContact] = useState<Contact | null>(null);

  useEffect(() => {
    loadContacts();
  }, []);

  const loadContacts = async () => {
    setIsLoading(true);
    try {
      const data = await getContacts();
      setContacts(data);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDelete = async (contactId: string) => {
    if (window.confirm('确定要删除这个联系人吗？')) {
      await deleteContact(contactId);
      loadContacts();
    }
  };

  const handleEdit = (contact: Contact) => {
    setEditingContact(contact);
    setShowModal(true);
  };

  const handleAdd = () => {
    setEditingContact(null);
    setShowModal(true);
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-fade-in-up">
      {/* 页面标题 */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">紧急联系人</h1>
          <p className="text-sm text-[var(--color-text-muted)] mt-1">
            管理紧急联系人和联系方式
          </p>
        </div>
        <button
          onClick={handleAdd}
          className="flex items-center gap-2 px-4 py-2 bg-[var(--color-primary)] text-white rounded-xl font-medium text-sm hover:opacity-90 transition-colors btn-press shadow-md"
        >
          <Plus className="w-4 h-4" />
          添加联系人
        </button>
      </div>

      {/* 联系人列表 */}
      <div className="space-y-4">
        {isLoading ? (
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[var(--color-border)] animate-pulse">
            <div className="h-4 bg-[var(--color-bg-tertiary)] rounded w-1/4 mb-4" />
            <div className="h-3 bg-[var(--color-bg-tertiary)] rounded w-3/4" />
          </div>
        ) : contacts.length > 0 ? (
          contacts.map((contact, index) => (
            <ContactCard
              key={contact.id}
              contact={contact}
              onEdit={() => handleEdit(contact)}
              onDelete={() => handleDelete(contact.id)}
              style={{ animationDelay: `${index * 0.1}s` }}
            />
          ))
        ) : (
          <div className="bg-white rounded-2xl p-8 shadow-sm border border-[var(--color-border)] text-center">
            <User className="w-12 h-12 mx-auto mb-4 text-[var(--color-text-muted)] opacity-50" />
            <p className="text-[var(--color-text-muted)]">暂无紧急联系人</p>
            <button
              onClick={handleAdd}
              className="text-[var(--color-primary)] hover:underline mt-2"
            >
              添加第一个联系人
            </button>
          </div>
        )}
      </div>

      {/* 添加/编辑模态框 */}
      {showModal && (
        <ContactModal
          contact={editingContact}
          onClose={() => {
            setShowModal(false);
            setEditingContact(null);
          }}
          onSave={() => {
            setShowModal(false);
            setEditingContact(null);
            loadContacts();
          }}
        />
      )}
    </div>
  );
}

/**
 * 联系人卡片组件
 */
function ContactCard({
  contact,
  onEdit,
  onDelete,
  style,
}: {
  contact: Contact;
  onEdit: () => void;
  onDelete: () => void;
  style?: React.CSSProperties;
}) {
  return (
    <div
      className="bg-white rounded-2xl p-4 shadow-sm border border-[var(--color-border)] card-interactive animate-card-list-in"
      style={style}
    >
      <div className="flex items-start gap-4">
        {/* 头像 */}
        <div className={`w-12 h-12 rounded-full flex items-center justify-center ${
          contact.isEmergency
            ? 'bg-[var(--color-danger-bg)]'
            : 'bg-[var(--color-bg-tertiary)]'
        }`}>
          <User className={`w-6 h-6 ${
            contact.isEmergency
              ? 'text-[var(--color-danger)]'
              : 'text-[var(--color-text-muted)]'
          }`} />
        </div>

        {/* 联系人信息 */}
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <h3 className="text-base font-semibold text-[var(--color-text-primary)]">
              {contact.name}
            </h3>
            {contact.isEmergency && (
              <span className="px-2 py-0.5 rounded text-xs font-medium bg-[var(--color-danger-bg)] text-[var(--color-danger)]">
                紧急联系人
              </span>
            )}
          </div>
          <div className="flex items-center gap-1 text-sm text-[var(--color-text-secondary)]">
            <Phone className="w-4 h-4" />
            <span>{contact.phone}</span>
          </div>
          {contact.relationship && (
            <p className="text-xs text-[var(--color-text-muted)] mt-1">
              关系: {contact.relationship}
            </p>
          )}
        </div>

        {/* 操作按钮 */}
        <div className="flex items-center gap-1">
          <button
            onClick={onEdit}
            className="p-2 rounded-lg text-[var(--color-text-muted)] hover:bg-[var(--color-bg-tertiary)] transition-colors"
            title="编辑"
          >
            <Edit2 className="w-5 h-5" />
          </button>
          <button
            onClick={onDelete}
            className="p-2 rounded-lg text-[var(--color-danger)] hover:bg-[var(--color-danger-bg)] transition-colors"
            title="删除"
          >
            <Trash2 className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  );
}

/**
 * 联系人添加/编辑模态框
 */
function ContactModal({
  contact,
  onClose,
  onSave,
}: {
  contact: Contact | null;
  onClose: () => void;
  onSave: () => void;
}) {
  const [name, setName] = useState(contact?.name || '');
  const [phone, setPhone] = useState(contact?.phone || '');
  const [relationship, setRelationship] = useState(contact?.relationship || '');
  const [isEmergency, setIsEmergency] = useState(contact?.isEmergency || false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name.trim()) {
      setError('请输入联系人姓名');
      return;
    }
    if (!phone.trim()) {
      setError('请输入联系电话');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      if (contact) {
        await updateContact(contact.id, {
          name: name.trim(),
          phone: phone.trim(),
          relation: relationship.trim() || undefined,
        });
      } else {
        await createContact({
          name: name.trim(),
          phone: phone.trim(),
          relation: relationship.trim() || undefined,
        });
      }
      onSave();
    } catch (err) {
      setError(err instanceof Error ? err.message : '保存失败');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div className="absolute inset-0 bg-black/50" onClick={onClose} />
      <div className="relative bg-white rounded-2xl shadow-xl w-full max-w-md animate-fade-in-up">
        {/* 头部 */}
        <div className="p-6 border-b border-[var(--color-border)] flex items-center justify-between">
          <h3 className="text-lg font-bold text-[var(--color-text-primary)]">
            {contact ? '编辑联系人' : '添加联系人'}
          </h3>
          <button
            onClick={onClose}
            className="p-2 rounded-lg hover:bg-[var(--color-bg-tertiary)] transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 表单 */}
        <form onSubmit={handleSubmit}>
          <div className="p-6 space-y-4">
            {error && (
              <div className="flex items-center gap-2 p-3 bg-[var(--color-danger-bg)] rounded-xl text-sm text-[var(--color-danger)]">
                <AlertCircle className="w-4 h-4 flex-shrink-0" />
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                姓名 *
              </label>
              <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="请输入联系人姓名"
                className="w-full px-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                电话 *
              </label>
              <input
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="请输入联系电话"
                className="w-full px-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
                required
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-[var(--color-text-secondary)] mb-2">
                关系
              </label>
              <input
                type="text"
                value={relationship}
                onChange={(e) => setRelationship(e.target.value)}
                placeholder="例如：儿子、女儿、医生"
                className="w-full px-4 py-3 bg-[var(--color-bg-secondary)] border border-[var(--color-border)] rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] focus:border-transparent"
              />
            </div>

            <div className="flex items-center gap-3">
              <button
                type="button"
                onClick={() => setIsEmergency(!isEmergency)}
                className={`relative w-12 h-6 rounded-full transition-colors ${
                  isEmergency ? 'bg-[var(--color-danger)]' : 'bg-[var(--color-bg-tertiary)]'
                }`}
              >
                <span
                  className={`absolute top-1 left-1 w-4 h-4 rounded-full bg-white shadow transition-transform ${
                    isEmergency ? 'translate-x-6' : ''
                  }`}
                />
              </button>
              <span className="text-sm text-[var(--color-text-secondary)]">
                设为紧急联系人
              </span>
            </div>
          </div>

          {/* 操作按钮 */}
          <div className="p-6 border-t border-[var(--color-border)] flex gap-3">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-3 text-sm font-medium text-[var(--color-text-secondary)] bg-[var(--color-bg-secondary)] rounded-xl hover:bg-[var(--color-bg-tertiary)] transition-colors btn-press"
            >
              取消
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="flex-1 px-4 py-3 text-sm font-medium text-white bg-[var(--color-primary)] rounded-xl hover:opacity-90 transition-colors btn-press disabled:opacity-50"
            >
              {isSubmitting ? '保存中...' : '保存'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}