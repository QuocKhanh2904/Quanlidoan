CREATE TRIGGER trg_UpdateDoAnStatus
ON DANGKY
AFTER INSERT, DELETE
AS
BEGIN
    SET NOCOUNT ON;

    -- Cập nhật trạng thái = 2 nếu có ít nhất 1 đăng ký
    UPDATE DOAN
    SET TrangThai = 2
    WHERE MaDA IN (
        SELECT DISTINCT MaDA FROM DANGKY
    );

    -- Cập nhật trạng thái = 1 nếu không có đăng ký nào
    UPDATE DOAN
    SET TrangThai = 1
    WHERE MaDA NOT IN (
        SELECT DISTINCT MaDA FROM DANGKY
    );
END;



