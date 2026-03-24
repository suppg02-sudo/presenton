const layoutId = "blank";
const layoutName = "Blank";
const layoutDescription = "Empty slide canvas";

const Schema = z.object({
  background_color: z.enum(['white', 'purple', 'light-gray']).default('white').describe('Background color')
});

const dynamicSlideLayout = ({ data }) => {
  const { background_color = 'white' } = data || {};

  const colors = {
    'white': '#FFFFFF',
    'purple': '#8F1A95',
    'light-gray': '#F5F5F5'
  };

  const containerStyle = {
    width: '100%',
    height: '100vh',
    backgroundColor: colors[background_color],
    display: 'flex',
    flexDirection: 'column',
    justifyContent: 'center',
    alignItems: 'center'
  };

  return (
    <div style={containerStyle} data-layout="blank">
    </div>
  );
};

