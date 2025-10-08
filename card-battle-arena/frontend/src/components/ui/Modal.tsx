import React, { useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { createPortal } from 'react-dom'
import { cn } from '@/utils/classnames'

interface ModalProps {
  isOpen: boolean
  onClose: () => void
  title?: string
  children: React.ReactNode
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  closeOnBackdropClick?: boolean
  closeOnEscape?: boolean
  showCloseButton?: boolean
  className?: string
}

const Modal: React.FC<ModalProps> = ({
  isOpen,
  onClose,
  title,
  children,
  size = 'md',
  closeOnBackdropClick = true,
  closeOnEscape = true,
  showCloseButton = true,
  className,
}) => {
  useEffect(() => {
    const handleEscape = (event: KeyboardEvent) => {
      if (closeOnEscape && event.key === 'Escape') {
        onClose()
      }
    }

    if (isOpen) {
      document.addEventListener('keydown', handleEscape)
      document.body.style.overflow = 'hidden'
    }

    return () => {
      document.removeEventListener('keydown', handleEscape)
      document.body.style.overflow = 'unset'
    }
  }, [isOpen, closeOnEscape, onClose])

  if (!isOpen) return null

  const sizeClasses = {
    sm: 'max-w-md',
    md: 'max-w-lg',
    lg: 'max-w-2xl',
    xl: 'max-w-4xl',
    full: 'max-w-full mx-4',
  }

  const modalContent = (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 overflow-y-auto"
      >
        {/* 背景遮罩 */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 bg-black bg-opacity-50 backdrop-blur-sm"
          onClick={closeOnBackdropClick ? onClose : undefined}
        />

        {/* 模态框容器 */}
        <div className="flex min-h-full items-center justify-center p-4">
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            transition={{ duration: 0.2, ease: 'easeOut' }}
            className={cn(
              'relative w-full rounded-lg bg-gray-800 shadow-2xl border border-gray-700',
              sizeClasses[size],
              className
            )}
          >
            {/* 模态框头部 */}
            {(title || showCloseButton) && (
              <div className="flex items-center justify-between p-6 border-b border-gray-700">
                {title && (
                  <h2 className="text-xl font-semibold text-white">
                    {title}
                  </h2>
                )}
                {showCloseButton && (
                  <button
                    onClick={onClose}
                    className="text-gray-400 hover:text-white transition-colors p-1 hover:bg-gray-700 rounded"
                  >
                    <svg
                      className="w-6 h-6"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M6 18L18 6M6 6l12 12"
                      />
                    </svg>
                  </button>
                )}
              </div>
            )}

            {/* 模态框内容 */}
            <div className="p-6">
              {children}
            </div>
          </motion.div>
        </div>
      </motion.div>
    </AnimatePresence>
  )

  return createPortal(modalContent)
}

interface ModalHeaderProps {
  title?: string
  description?: string
  onClose?: () => void
  children?: React.ReactNode
  className?: string
}

export const ModalHeader: React.FC<ModalHeaderProps> = ({
  title,
  description,
  onClose,
  children,
  className,
}) => (
  <div className={cn('flex items-start justify-between', className)}>
    <div>
      {title && (
        <h3 className="text-lg font-semibold text-white">
          {title}
        </h3>
      )}
      {description && (
        <p className="text-sm text-gray-400 mt-1">
          {description}
        </p>
      )}
    </div>
    <div className="flex items-center space-x-2">
      {children}
      {onClose && (
        <button
          onClick={onClose}
          className="text-gray-400 hover:text-white transition-colors p-1 hover:bg-gray-700 rounded"
        >
          <svg
            className="w-5 h-5"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M6 18L18 6M6 6l12 12"
            />
          </svg>
        </button>
      )}
    </div>
  </div>
)

interface ModalBodyProps {
  children: React.ReactNode
  className?: string
}

export const ModalBody: React.FC<ModalBodyProps> = ({ children, className }) => (
  <div className={cn('flex-1', className)}>
    {children}
  </div>
)

interface ModalFooterProps {
  children: React.ReactNode
  className?: string
}

export const ModalFooter: React.FC<ModalFooterProps> = ({ children, className }) => (
  <div className={cn('flex items-center justify-end space-x-3 pt-4 border-t border-gray-700', className)}>
    {children}
  </div>
)

interface ConfirmModalProps extends Omit<ModalProps, 'title' | 'children'> {
  message: string
  confirmText?: string
  cancelText?: string
  onConfirm: () => void
  onCancel?: () => void
  variant?: 'primary' | 'danger' | 'warning'
}

export const ConfirmModal: React.FC<ConfirmModalProps> = ({
  message,
  confirmText = '确认',
  cancelText = '取消',
  onConfirm,
  onCancel,
  variant = 'primary',
  ...modalProps
}) => {
  const variantClasses = {
    primary: 'bg-primary-600 hover:bg-primary-700',
    danger: 'bg-red-600 hover:bg-red-700',
    warning: 'bg-yellow-600 hover:bg-yellow-700',
  }

  return (
    <Modal {...modalProps}>
      <ModalBody>
        <p className="text-gray-300">{message}</p>
      </ModalBody>
      <ModalFooter>
        <Button
          variant="outline"
          onClick={onCancel || modalProps.onClose}
        >
          {cancelText}
        </Button>
        <Button
          variant={variant}
          onClick={onConfirm}
          className={variantClasses[variant]}
        >
          {confirmText}
        </Button>
      </ModalFooter>
    </Modal>
  )
}

interface LoadingModalProps extends Omit<ModalProps, 'children'> {
  message?: string
}

export const LoadingModal: React.FC<LoadingModalProps> = ({
  message = '加载中...',
  ...modalProps
}) => (
  <Modal
    {...modalProps}
    showCloseButton={false}
    closeOnBackdropClick={false}
    closeOnEscape={false}
  >
    <ModalBody>
      <div className="flex flex-col items-center justify-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-500 mb-4"></div>
        <p className="text-gray-300">{message}</p>
      </div>
    </ModalBody>
  </Modal>
)

export default Modal