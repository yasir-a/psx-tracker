import React, { useEffect, useState } from 'react';
import { Card } from '../../ui/Card';
import { Badge } from '../../ui/Badge';
import { Button } from '../../ui/Button';
import { Input } from '../../ui/Input';
import { adminService, AdminUserItem } from '../../../services/adminService';
import { useAuth } from '../../../contexts/AuthContext';
import { ShieldCheck, Key, Trash2, Search, Loader2, AlertTriangle } from 'lucide-react';

export const AdminView: React.FC = () => {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<AdminUserItem[]>([]);
  const [search, setSearch] = useState('');
  const [isLoading, setIsLoading] = useState(true);
  const [page, setPage] = useState(1);
  const [actionError, setActionError] = useState<string | null>(null);
  const [actionSuccess, setActionSuccess] = useState<string | null>(null);

  // Modals
  const [resetTarget, setResetTarget] = useState<AdminUserItem | null>(null);
  const [newPassword, setNewPassword] = useState('');
  const [isResetting, setIsResetting] = useState(false);

  const [deleteTarget, setDeleteTarget] = useState<AdminUserItem | null>(null);
  const [isDeleting, setIsDeleting] = useState(false);

  const fetchUsers = async (targetPage = 1, searchQuery = search) => {
    setIsLoading(true);
    setActionError(null);
    try {
      const res = await adminService.listUsers(targetPage, searchQuery.trim() || undefined);
      setUsers(res.users);
      setPage(res.pagination.page);
    } catch (err: any) {
      setActionError(err?.response?.data?.error?.message || 'Failed to load user directory.');
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers(1);
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    fetchUsers(1, search);
  };

  const handleResetPassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!resetTarget || !newPassword) return;
    setIsResetting(true);
    setActionError(null);
    try {
      await adminService.resetPassword(resetTarget.id, newPassword);
      setActionSuccess(`Password reset successfully for ${resetTarget.email}. User sessions terminated.`);
      setResetTarget(null);
      setNewPassword('');
    } catch (err: any) {
      setActionError(err?.response?.data?.error?.message || 'Failed to reset password.');
    } finally {
      setIsResetting(false);
    }
  };

  const handleDeleteUser = async () => {
    if (!deleteTarget) return;
    setIsDeleting(true);
    setActionError(null);
    try {
      await adminService.deleteUser(deleteTarget.id);
      setActionSuccess(`User ${deleteTarget.email} and all associated data permanently deleted.`);
      setDeleteTarget(null);
      fetchUsers(page);
    } catch (err: any) {
      setActionError(err?.response?.data?.error?.message || 'Failed to delete user.');
    } finally {
      setIsDeleting(false);
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="flex items-center gap-2 text-2xl font-bold text-gray-900">
            <ShieldCheck className="w-6 h-6 text-emerald-600" />
            Admin User Management
          </h2>
          <p className="text-xs text-gray-500 mt-0.5">
            Directory of registered users. Perform password resets or cascading hard-deletions safely.
          </p>
        </div>
      </div>

      {actionSuccess && (
        <div className="flex justify-between p-3 text-sm border rounded-lg bg-emerald-50 border-emerald-200 text-emerald-800">
          <span>{actionSuccess}</span>
          <button onClick={() => setActionSuccess(null)} className="font-bold">×</button>
        </div>
      )}

      {actionError && (
        <div className="flex justify-between p-3 text-sm border rounded-lg bg-rose-50 border-rose-200 text-rose-800">
          <span>{actionError}</span>
          <button onClick={() => setActionError(null)} className="font-bold">×</button>
        </div>
      )}

      <Card>
        <form onSubmit={handleSearch} className="flex max-w-md gap-2 mb-4">
          <Input
            placeholder="Search by name or email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
          <Button type="submit" variant="primary">
            <Search className="w-4 h-4 mr-1" />
            Search
          </Button>
        </form>

        {isLoading ? (
          <div className="flex flex-col items-center justify-center py-16 text-gray-500">
            <Loader2 className="w-8 h-8 mb-3 animate-spin text-emerald-600" />
            <p className="text-xs font-semibold">Loading user directory...</p>
          </div>
        ) : users.length === 0 ? (
          <div className="py-12 text-sm text-center text-gray-500">No users found.</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm text-left whitespace-nowrap">
              <thead className="text-xs font-semibold tracking-wider text-gray-500 uppercase bg-gray-50">
                <tr>
                  <th className="px-4 py-3">User</th>
                  <th className="px-4 py-3">Email</th>
                  <th className="px-4 py-3">Role</th>
                  <th className="px-4 py-3">Portfolios</th>
                  <th className="px-4 py-3">Registered</th>
                  <th className="px-4 py-3 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {users.map((u) => {
                  const isSelf = currentUser?.id === u.id;
                  return (
                    <tr key={u.id} className="transition-colors hover:bg-gray-50">
                      <td className="px-4 py-3.5 font-bold text-gray-900 flex items-center gap-2">
                        <div className="flex items-center justify-center text-xs font-bold text-gray-700 bg-gray-200 rounded-full w-7 h-7">
                          {u.full_name.charAt(0).toUpperCase()}
                        </div>
                        {u.full_name}
                        {isSelf && (
                          <span className="text-[10px] bg-blue-100 text-blue-800 px-1.5 py-0.5 rounded font-medium">
                            You
                          </span>
                        )}
                      </td>
                      <td className="px-4 py-3.5 text-gray-600">{u.email}</td>
                      <td className="px-4 py-3.5">
                        <Badge variant={u.role === 'admin' ? 'blue' : 'gray'}>
                          {u.role.toUpperCase()}
                        </Badge>
                      </td>
                      <td className="px-4 py-3.5 text-gray-600">{u.portfolio_count}</td>
                      <td className="px-4 py-3.5 text-gray-500">
                        {new Date(u.created_at).toLocaleDateString()}
                      </td>
                      <td className="px-4 py-3.5 text-right space-x-2">
                        <Button
                          size="sm"
                          variant="secondary"
                          onClick={() => {
                            setResetTarget(u);
                            setNewPassword('');
                          }}
                          className="inline-flex items-center gap-1"
                        >
                          <Key className="w-3.5 h-3.5 text-amber-600" />
                          Reset Password
                        </Button>
                        <Button
                          size="sm"
                          variant="danger"
                          disabled={isSelf}
                          onClick={() => setDeleteTarget(u)}
                          className="inline-flex items-center gap-1 disabled:opacity-30"
                          title={isSelf ? 'Cannot delete yourself' : 'Delete user permanently'}
                        >
                          <Trash2 className="w-3.5 h-3.5" />
                          Delete
                        </Button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </Card>

      {/* Password Reset Modal */}
      {resetTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="w-full max-w-md p-6 bg-white shadow-xl rounded-xl">
            <h3 className="flex items-center gap-2 mb-2 text-lg font-bold text-gray-900">
              <Key className="w-5 h-5 text-amber-600" />
              Reset Password for {resetTarget.full_name}
            </h3>
            <p className="mb-4 text-xs text-gray-500">
              Enter a new secure password. All active login sessions for <strong>{resetTarget.email}</strong> will be invalidated immediately.
            </p>
            <form onSubmit={handleResetPassword} className="space-y-4">
              <div>
                <label className="block mb-1 text-xs font-semibold text-gray-700">New Password</label>
                <Input
                  type="password"
                  placeholder="Min 8 chars, letters and numbers"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                  required
                />
              </div>
              <div className="flex justify-end gap-2 pt-2">
                <Button type="button" variant="secondary" onClick={() => setResetTarget(null)}>
                  Cancel
                </Button>
                <Button type="submit" variant="primary" disabled={isResetting || !newPassword}>
                  {isResetting ? 'Resetting...' : 'Confirm Reset'}
                </Button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Hard Delete Confirmation Modal */}
      {deleteTarget && (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50">
          <div className="w-full max-w-md p-6 bg-white border-t-4 shadow-xl rounded-xl border-rose-600">
            <h3 className="flex items-center gap-2 mb-2 text-lg font-bold text-gray-900 text-rose-700">
              <AlertTriangle className="w-5 h-5 text-rose-600" />
              Permanently Delete User?
            </h3>
            <p className="mb-3 text-sm text-gray-700">
              Are you sure you want to permanently delete <strong>{deleteTarget.full_name}</strong> ({deleteTarget.email})?
            </p>
            <div className="p-3 mb-4 space-y-1 text-xs border rounded-lg bg-rose-50 border-rose-200 text-rose-800">
              <p className="font-bold">This action cannot be undone.</p>
              <p>
                All portfolios, broker accounts, transactions, tax lots, cash ledgers, and corporate actions owned by this user will be permanently destroyed from the database.
              </p>
            </div>
            <div className="flex justify-end gap-2">
              <Button type="button" variant="secondary" onClick={() => setDeleteTarget(null)} disabled={isDeleting}>
                Cancel
              </Button>
              <Button type="button" variant="danger" onClick={handleDeleteUser} disabled={isDeleting}>
                {isDeleting ? 'Deleting All Data...' : 'Yes, Delete Permanently'}
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};