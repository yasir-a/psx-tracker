import React, { useState } from 'react';
import { Modal } from '../../ui/Modal';
import { Input } from '../../ui/Input';
import { Button } from '../../ui/Button';
import { portfolioService } from '../../../services/portfolioService';

interface CreatePortfolioModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess: (newPortfolioId: string) => void;
}

export const CreatePortfolioModal: React.FC<CreatePortfolioModalProps> = ({
  isOpen,
  onClose,
  onSuccess,
}) => {
  const [name, setName] = useState('');
  const [description, setDescription] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setIsLoading(true);

    try {
      const created = await portfolioService.createPortfolio({
        name: name.trim(),
        description: description.trim() || undefined,
      });
      onSuccess(created.id);
      setName('');
      setDescription('');
      onClose();
    } catch (err: any) {
      setError(err?.response?.data?.error?.message || 'Failed to create account');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Add Broker / CDC Account">
      {error && (
        <div className="mb-4 p-3 rounded-lg bg-rose-50 border border-rose-200 text-rose-700 text-xs">
          {error}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Account / Broker Name"
          placeholder="e.g. Darson Securities, BMA Capital, CDC Investor Account"
          value={name}
          onChange={(e) => setName(e.target.value)}
          required
        />

        <Input
          label="Description / Account Number (Optional)"
          placeholder="e.g. CDC IAS Account # 123456"
          value={description}
          onChange={(e) => setDescription(e.target.value)}
        />

        <div className="pt-2">
          <Button type="submit" className="w-full" isLoading={isLoading}>
            Create Account
          </Button>
        </div>
      </form>
    </Modal>
  );
};